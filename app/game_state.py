"""
Gestión del estado del juego con persistencia en DynamoDB (SpacegomGames).

Persistencia en tabla SpacegomGames (Single Table Design):
- PK=game_id (GAME#<id>), SK=entity_id.
- METADATA: estado base (sin events, dice_rolls, transactions, event_logs).
- LOG#<tipo>#<timestamp>#<i>: eventos, tiradas, transacciones, logs UI.

Sin escritura a disco; logs del sistema a stdout para CloudWatch.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.aws_client import (
    get_games_table,
    item_from_decimal,
    item_to_decimal,
)

_BULK_KEYS = ("events", "dice_rolls", "transactions", "event_logs")


def _pk(game_id: str) -> str:
    return f"GAME#{game_id}"


class GameState:
    """
    Maneja el estado del juego con persistencia en DynamoDB (SpacegomGames).

    Carga/guarda METADATA y LOG# en SpacegomGames. Sin archivos en disco.
    """

    def __init__(self, game_id: str) -> None:
        self.game_id = game_id
        self._table = get_games_table()
        self.state, self.personnel, self.missions, self.trade_orders, self.employee_tasks = self._load_or_create()

    def _load_or_create(self) -> tuple[Dict[str, Any], List[Dict], List[Dict], List[Dict], List[Dict]]:
        """Carga desde DynamoDB o crea estado por defecto. Retorna (state, personnel, missions, orders, tasks)."""
        pk = _pk(self.game_id)
        resp = self._table.query(KeyConditionExpression="game_id = :pk", ExpressionAttributeValues={":pk": pk})
        items = [item_from_decimal(i) for i in resp.get("Items", [])]
        while "LastEvaluatedKey" in resp:
            resp = self._table.query(
                KeyConditionExpression="game_id = :pk",
                ExpressionAttributeValues={":pk": pk},
                ExclusiveStartKey=resp["LastEvaluatedKey"],
            )
            items.extend([item_from_decimal(i) for i in resp.get("Items", [])])

        metadata = next((i for i in items if i.get("entity_id") == "METADATA"), None)
        if not metadata:
            defs = self._create_default_state()
            return defs, [], [], [], []

        state = {k: v for k, v in metadata.items() if k not in ("game_id", "entity_id")}
        for key in _BULK_KEYS:
            state.setdefault(key, [])

        log_items = [i for i in items if (i.get("entity_id") or "").startswith("LOG#")]
        for it in log_items:
            eid = it["entity_id"]
            parts = eid.split("#")
            if len(parts) < 3:
                continue
            tipo = parts[1]
            payload = {k: v for k, v in it.items() if k not in ("game_id", "entity_id")}
            if tipo == "dice":
                state["dice_rolls"].append(payload)
            elif tipo == "tx":
                state["transactions"].append(payload)
            elif tipo == "sys":
                state["events"].append(payload)
            elif tipo == "ui":
                state["event_logs"].append(payload)

        for key in _BULK_KEYS:
            state[key] = state.get(key) or []

        personnel = []
        missions = []
        orders = []
        tasks = []
        for it in items:
            eid = (it.get("entity_id") or "")
            payload = {k: v for k, v in it.items() if k not in ("game_id", "entity_id")}
            if "id" not in payload and "#" in eid:
                try:
                    payload["id"] = int(eid.split("#", 1)[1])
                except (IndexError, ValueError):
                    pass
            if eid.startswith("PERSONNEL#"):
                personnel.append(payload)
            elif eid.startswith("MISSION#"):
                missions.append(payload)
            elif eid.startswith("ORDER#"):
                orders.append(payload)
            elif eid.startswith("TASK#"):
                tasks.append(payload)

        return state, personnel, missions, orders, tasks
    
    def _create_default_state(self) -> Dict[str, Any]:
        """
        Crea el estado por defecto de una nueva partida.
        
        Inicializa todos los campos del estado con valores por defecto.
        Este estado incluye:
        - Setup: Área, densidad de mundos, posición inicial
        - Compañía/Nave: Nombres, modelo, pasajeros
        - HUD: Combustible, almacenamiento, mes, reputación
        - Calendario: Año, mes, día, cola de eventos
        - Daños: Sistema de daños leves/moderados/graves
        - Navegación: Planetas descubiertos, cuadrantes explorados
        - Economía: Dificultad, tesorería, transacciones
        - Historial: Eventos y tiradas de dados
        
        Returns:
            Diccionario con el estado inicial completo
        """
        return {
            "game_id": self.game_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            
            # Setup inicial - Determinado durante la creación de la partida
            "area": None,  # Área espacial (2-12 desde tirada 2d6)
            "world_density": None,  # "Baja", "Media", "Alta" (desde 2d6)
            "setup_complete": False,  # Flag de setup completado
            "ship_row": None,  # Fila inicial de la nave (1-6)
            "ship_col": None,  # Columna inicial de la nave (1-6)
            "ship_pos_complete": False,  # Flag de posición establecida
            "ship_location_on_planet": "Mundo",  # "Mundo", "Espaciopuerto", "Instalación", "Estación"
            
            # Compañía y Nave - Identidad de la partida
            "company_name": "Nueva Compañía",
            "ship_name": "Fénix Dorado",
            "ship_model": "Basic Starfall",  # Modelo inicial heredado
            "passengers": 0,  # Pasajeros actuales a bordo
            
            # HUD - Estado crítico visible en el dashboard
            "fuel": 18,  # Combustible actual
            "fuel_max": 30,  # Capacidad máxima de combustible
            "storage": 0,  # Almacenamiento usado (UCN)
            "storage_max": 40,  # Capacidad máxima de almacenamiento
            "month": 1,  # Mes actual del juego
            "reputation": 0,  # Reputación actual
            
            # Sistema de Calendario (35 días/mes, 12 meses/año)
            "year": 1,  # Año actual del juego
            "day": 1,  # Día actual del mes (1-35)
            "event_queue": [],  # Cola ordenada de eventos futuros [{type, date, data}]
            
            # Sistema de Daños - Estado de la nave
            "damages": {
                "light": False,  # Daños leves activos
                "moderate": False,  # Daños moderados activos
                "severe": False,  # Daños graves activos
                "counts": {
                    "light": 0,  # Contador de daños leves acumulados
                    "moderate": 0,  # Contador de daños moderados acumulados
                    "severe": 0  # Contador de daños graves acumulados
                }
            },
            
            # Navegación - Exploración y descubrimientos
            "current_planet_code": None,  # Código del planeta actual (111-666)
            "starting_planet_code": None,  # Código del planeta inicial
            "current_area": None,  # Área actual (puede cambiar durante el juego)
            "explored_quadrants": [],  # Lista de coordenadas exploradas ["1,2", "1,3"]
            "quadrant_planets": {},  # Mapeo {"row,col": planet_code}
            "discovered_planets": {},  # Registro completo {"planet_code": {"area": int, "quadrant": "row,col"}}
            
            "difficulty": None,
            "treasury": 0,
            "reputation": 0,
            "last_personnel_id": 0,
            "last_mission_id": 0,
            "last_order_id": 0,
            "last_task_id": 0,

            # Historial de Transacciones
            "transactions": [],  # [{date, amount, description, category}]
            
            # Nota: El personal se gestiona en la base de datos (tabla Personnel)
            # Los datos de la tripulación se consultan desde la BD, no se almacenan en el estado
            
            # Comercio - Carga actual
            "cargo": {},  # {product_code: quantity} - Productos en la bodega
            
            # Historial - Eventos y tiradas de dados
            "events": [],
            "dice_rolls": [],
            "event_logs": [],  # EventLogger

            "passenger_transport_available": True
        }
    
    def _save_metadata(self) -> None:
        """Escribe solo METADATA en DynamoDB (sin listas pesadas)."""
        self.state["updated_at"] = datetime.now().isoformat()
        meta = {k: v for k, v in self.state.items() if k not in _BULK_KEYS}
        meta["game_id"] = _pk(self.game_id)
        meta["entity_id"] = "METADATA"
        self._table.put_item(Item=item_to_decimal(meta))

    def save(self) -> None:
        """Persiste el estado (METADATA) en DynamoDB. Sin escritura a disco."""
        self._save_metadata()
    
    def get_adjacent_coordinates(self, row: int, col: int, jump_range: int = 1) -> List[Dict[str, Any]]:
        """
        Calcula coordenadas alcanzables dentro del rango de salto.
        
        Incluye transiciones entre áreas (columna A conecta con área anterior,
        columna F conecta con área siguiente). El sistema de coordenadas usa
        1-based para display pero cálculos internos pueden ser 0-based.
        
        Args:
            row: Fila actual (1-6)
            col: Columna actual (1-6, donde 1=A, 6=F)
            jump_range: Rango de salto (default: 1)
        
        Returns:
            Lista de diccionarios con coordenadas alcanzables, cada uno contiene:
            - area: Área de destino
            - row: Fila de destino
            - col: Columna de destino
            - col_letter: Letra de la columna (A-F)
        
        Note:
            Las coordenadas en los bordes pueden cambiar de área si hay conexión.
            Las filas no tienen transiciones entre áreas.
        """
        reachable = []
        current_area = self.state.get("area")
        
        # Implementación para jump_range 1 (movimiento estándar en grid 1-6)
        for dr in range(-jump_range, jump_range + 1):
            for dc in range(-jump_range, jump_range + 1):
                if dr == 0 and dc == 0:
                    continue  # Saltar la posición actual
                
                target_r = row + dr
                target_c = col + dc
                target_area = current_area
                
                # Verificar transiciones de columna entre áreas
                if target_c < 1:  # Izquierda de Columna A
                    if current_area > 2:
                        target_area = current_area - 1
                        target_c = 6  # Se convierte en Columna F del área anterior
                    else:
                        continue  # Bloqueado (izquierda del área 2)
                elif target_c > 6:  # Derecha de Columna F
                    if current_area < 12:
                        target_area = current_area + 1
                        target_c = 1  # Se convierte en Columna A del área siguiente
                    else:
                        continue  # Bloqueado (derecha del área 12)
                
                # Verificar límites de fila (no hay transiciones de fila entre áreas)
                if 1 <= target_r <= 6:
                    reachable.append({
                        "area": target_area,
                        "row": target_r,
                        "col": target_c,
                        "col_letter": chr(64 + target_c)  # Convierte 1-6 a A-F
                    })
                    
        return reachable
    
    def update(self, **kwargs) -> None:
        """
        Actualiza múltiples campos del estado y guarda automáticamente.
        
        Solo actualiza campos que ya existen en el estado. Si se intenta
        actualizar un campo que no existe, se ignora silenciosamente.
        
        Args:
            **kwargs: Pares clave-valor con los campos a actualizar
        
        Example:
            >>> game.update(treasury=500, fuel=25)
            # Actualiza treasury y fuel, luego guarda automáticamente
        """
        for key, value in kwargs.items():
            if key in self.state:
                self.state[key] = value
        self.save()
    
    def _put_log(self, tipo: str, payload: Dict[str, Any]) -> None:
        """Escribe un ítem LOG#<tipo>#<ts>#<i> en DynamoDB."""
        ts = payload.get("timestamp", datetime.now().isoformat())
        idx = len(self.state["dice_rolls"] if tipo == "dice" else
                  self.state["transactions"] if tipo == "tx" else
                  self.state["events"] if tipo == "sys" else
                  self.state["event_logs"])
        entity_id = f"LOG#{tipo}#{ts}#{idx}"
        item = {"game_id": _pk(self.game_id), "entity_id": entity_id, **payload}
        self._table.put_item(Item=item_to_decimal(item))

    def add_event(self, event_type: str, description: str, data: Optional[Dict] = None) -> None:
        """Agrega un evento al historial y persiste como LOG#sys."""
        year = self.state.get("year", 1)
        month = self.state.get("month", 1)
        day = self.state.get("day", 1)
        game_date = f"{day:02d}-{month:02d}-{year}"
        ts = datetime.now().isoformat()
        event = {"timestamp": ts, "game_date": game_date, "type": event_type, "description": description, "data": data or {}}
        self.state["events"].append(event)
        self._put_log("sys", event)
        self._save_metadata()

    def record_dice_roll(self, num_dice: int, results: list, is_manual: bool, purpose: str = "") -> Dict[str, Any]:
        """Registra una tirada de dados y persiste como LOG#dice."""
        ts = datetime.now().isoformat()
        roll = {"timestamp": ts, "num_dice": num_dice, "results": results, "total": sum(results), "is_manual": is_manual, "purpose": purpose}
        self.state["dice_rolls"].append(roll)
        self._put_log("dice", roll)
        self._save_metadata()
        return roll

    def append_transaction(self, entry: Dict[str, Any]) -> None:
        """Añade una transacción y persiste como LOG#tx. No llama save()."""
        if "timestamp" not in entry:
            entry = {**entry, "timestamp": datetime.now().isoformat()}
        self.state.setdefault("transactions", []).append(entry)
        self._put_log("tx", entry)

    def append_event_log(self, entry: Dict[str, Any]) -> None:
        """Añade un log de UI (event_logs) y persiste como LOG#ui. No llama save()."""
        if "timestamp" not in entry:
            entry = {**entry, "timestamp": datetime.now().isoformat()}
        self.state.setdefault("event_logs", []).append(entry)
        self._put_log("ui", entry)

    def _next_id(self, key: str) -> int:
        """Incrementa last_<key>_id en state y retorna el nuevo valor."""
        k = f"last_{key}_id"
        self.state.setdefault(k, 0)
        self.state[k] += 1
        return self.state[k]

    def _put_entity(self, prefix: str, eid: int, data: Dict[str, Any]) -> None:
        """Escribe ítem ENTITY#<id> en DynamoDB."""
        doc = {"game_id": _pk(self.game_id), "entity_id": f"{prefix}#{eid}", **data}
        self._table.put_item(Item=item_to_decimal(doc))

    def _delete_entity(self, prefix: str, eid: int) -> None:
        """Elimina ítem ENTITY#<id>."""
        self._table.delete_item(Key={"game_id": _pk(self.game_id), "entity_id": f"{prefix}#{eid}"})

    # --- Personnel ---
    def get_personnel(self, active_only: bool = True) -> List[Dict[str, Any]]:
        out = self.personnel
        if active_only:
            out = [p for p in out if p.get("is_active", True)]
        return out

    def get_personnel_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        for p in self.personnel:
            if p.get("id") == uid:
                return p
        return None

    def add_personnel(self, data: Dict[str, Any]) -> int:
        uid = self._next_id("personnel")
        payload = {"id": uid, **data}
        self.personnel.append(payload)
        self._put_entity("PERSONNEL", uid, payload)
        self._save_metadata()
        return uid

    def update_personnel(self, uid: int, data: Dict[str, Any]) -> None:
        p = self.get_personnel_by_id(uid)
        if not p:
            return
        p.update(data)
        self._put_entity("PERSONNEL", uid, p)
        self._save_metadata()

    # --- Missions ---
    def get_missions(self) -> List[Dict[str, Any]]:
        return list(self.missions)

    def get_mission_by_id(self, mid: int) -> Optional[Dict[str, Any]]:
        for m in self.missions:
            if m.get("id") == mid:
                return m
        return None

    def add_mission(self, data: Dict[str, Any]) -> int:
        mid = self._next_id("mission")
        payload = {"id": mid, **data}
        self.missions.append(payload)
        self._put_entity("MISSION", mid, payload)
        self._save_metadata()
        return mid

    def update_mission(self, mid: int, data: Dict[str, Any]) -> None:
        m = self.get_mission_by_id(mid)
        if not m:
            return
        m.update(data)
        self._put_entity("MISSION", mid, m)
        self._save_metadata()

    def delete_mission(self, mid: int) -> None:
        self.missions[:] = [m for m in self.missions if m.get("id") != mid]
        self._delete_entity("MISSION", mid)
        self._save_metadata()

    # --- Trade orders ---
    def get_trade_orders(self) -> List[Dict[str, Any]]:
        return list(self.trade_orders)

    def get_order_by_id(self, oid: int) -> Optional[Dict[str, Any]]:
        for o in self.trade_orders:
            if o.get("id") == oid:
                return o
        return None

    def add_trade_order(self, data: Dict[str, Any]) -> int:
        oid = self._next_id("order")
        payload = {"id": oid, **data}
        self.trade_orders.append(payload)
        self._put_entity("ORDER", oid, payload)
        self._save_metadata()
        return oid

    def update_order(self, oid: int, data: Dict[str, Any]) -> None:
        o = self.get_order_by_id(oid)
        if not o:
            return
        o.update(data)
        self._put_entity("ORDER", oid, o)
        self._save_metadata()

    # --- Employee tasks ---
    def get_employee_tasks(self, employee_id: Optional[int] = None) -> List[Dict[str, Any]]:
        out = self.employee_tasks
        if employee_id is not None:
            out = [t for t in out if t.get("employee_id") == employee_id]
        return out

    def get_task_by_id(self, tid: int) -> Optional[Dict[str, Any]]:
        for t in self.employee_tasks:
            if t.get("id") == tid:
                return t
        return None

    def add_task(self, data: Dict[str, Any]) -> int:
        tid = self._next_id("task")
        payload = {"id": tid, **data}
        self.employee_tasks.append(payload)
        self._put_entity("TASK", tid, payload)
        self._save_metadata()
        return tid

    def update_task(self, tid: int, data: Dict[str, Any]) -> None:
        t = self.get_task_by_id(tid)
        if not t:
            return
        t.update(data)
        self._put_entity("TASK", tid, t)
        self._save_metadata()

    def delete_task(self, tid: int) -> None:
        self.employee_tasks[:] = [t for t in self.employee_tasks if t.get("id") != tid]
        self._delete_entity("TASK", tid)
        self._save_metadata()
    
    def explore_quadrant(self, row: int, col: int) -> None:
        """
        Marca un cuadrante como explorado y resetea flags de acciones.
        
        Cuando se explora un cuadrante, se marca en la lista de cuadrantes
        explorados y se resetean flags relacionados con el movimiento, como
        la disponibilidad de transporte de pasajeros.
        
        Args:
            row: Fila del cuadrante (1-6)
            col: Columna del cuadrante (1-6)
        """
        coord = f"{row},{col}"
        if coord not in self.state["explored_quadrants"]:
            self.state["explored_quadrants"].append(coord)
            
        # Resetear flags basados en movimiento
        self.state["passenger_transport_available"] = True
        self.save()
    
    def discover_planet(self, row: int, col: int, planet_code: int) -> None:
        """
        Registra el descubrimiento de un planeta en un cuadrante específico.
        
        Actualiza tanto el mapeo de cuadrantes a planetas como el registro
        completo de planetas descubiertos (Hoja de Mundos). Mantiene consistencia
        entre explored_quadrants y quadrant_planets.
        
        Args:
            row: Fila del cuadrante donde se descubrió (1-6)
            col: Columna del cuadrante donde se descubrió (1-6)
            planet_code: Código del planeta descubierto (111-666)
        """
        coord = f"{row},{col}"
        planet_code_str = str(planet_code)
        
        # Mapeo para el cuadrante (permite consulta rápida por coordenadas)
        self.state["quadrant_planets"][coord] = planet_code
        
        # Mapeo para el registro completo de mundos (Hoja de Mundos)
        if planet_code_str not in self.state["discovered_planets"]:
            self.state["discovered_planets"][planet_code_str] = {
                "area": self.state.get("area"),
                "quadrant": coord
            }
        
        self.save()

    def is_quadrant_explored(self, row: int, col: int) -> bool:
        """
        Verifica si un cuadrante ha sido explorado.
        
        Args:
            row: Fila del cuadrante (1-6)
            col: Columna del cuadrante (1-6)
        
        Returns:
            True si el cuadrante está en la lista de explorados
        """
        coord = f"{row},{col}"
        return coord in self.state["explored_quadrants"]
    
    @classmethod
    def list_games(cls) -> List[Dict[str, Any]]:
        """Lista partidas desde DynamoDB (Scan METADATA). Orden por updated_at descendente."""
        table = get_games_table()
        resp = table.scan(FilterExpression="entity_id = :eid", ExpressionAttributeValues={":eid": "METADATA"})
        items = resp.get("Items", [])
        while "LastEvaluatedKey" in resp:
            resp = table.scan(
                FilterExpression="entity_id = :eid",
                ExpressionAttributeValues={":eid": "METADATA"},
                ExclusiveStartKey=resp["LastEvaluatedKey"],
            )
            items.extend(resp.get("Items", []))

        games = []
        for it in items:
            d = item_from_decimal(it)
            raw_id = d.get("game_id", "")
            if raw_id.startswith("GAME#"):
                raw_id = raw_id[5:]
            games.append({
                "game_id": raw_id,
                "created_at": d.get("created_at"),
                "updated_at": d.get("updated_at"),
                "month": d.get("month", 1),
                "credits": d.get("treasury", 0),
            })
        return sorted(games, key=lambda x: (x["updated_at"] or ""), reverse=True)

    @classmethod
    def create_new_game(cls, game_name: Optional[str] = None) -> "GameState":
        """Crea una nueva partida (estado por defecto) y la persiste en DynamoDB."""
        if not game_name:
            game_name = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        game_id = "".join(c for c in game_name if c.isalnum() or c in ("_", "-")).lower()
        inst = cls(game_id)
        inst.save()
        return inst
