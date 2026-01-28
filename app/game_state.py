"""
Gestión del estado del juego con persistencia en archivos JSON.

Este módulo maneja la persistencia del estado del juego usando archivos JSON.
Cada partida tiene su propio directorio con un archivo `state.json` que contiene
todo el estado persistente.

Estructura del estado JSON:
    {
        "game_id": "string",
        "created_at": "ISO datetime",
        "updated_at": "ISO datetime",
        
        # Setup inicial
        "area": int,                    # Área espacial (2-12 desde 2d6)
        "world_density": str,           # "Baja", "Media", "Alta"
        "setup_complete": bool,
        "ship_row": int,                # Fila 1-6
        "ship_col": int,                # Columna 1-6
        "ship_location_on_planet": str, # "Mundo", "Espaciopuerto", etc.
        
        # Compañía y Nave
        "company_name": str,
        "ship_name": str,
        "ship_model": str,
        "passengers": int,
        
        # HUD - Estado crítico
        "fuel": int,
        "fuel_max": int,
        "storage": int,
        "storage_max": int,
        "month": int,
        "reputation": int,
        
        # Calendario (35 días/mes, 12 meses/año)
        "year": int,
        "day": int,
        "event_queue": List[Dict],      # Cola ordenada de eventos
        
        # Sistema de daños
        "damages": {
            "light": bool,
            "moderate": bool,
            "severe": bool,
            "counts": {"light": int, "moderate": int, "severe": int}
        },
        
        # Navegación
        "current_planet_code": int,
        "explored_quadrants": List[str],      # ["1,2", "1,3"]
        "quadrant_planets": Dict[str, int],    # {"row,col": planet_code}
        "discovered_planets": Dict[str, Dict], # {"planet_code": {"area": int, "quadrant": str}}
        
        # Economía
        "difficulty": str,               # "easy", "normal", "hard"
        "treasury": int,                 # Saldo en Créditos Spacegom (SC)
        "transactions": List[Dict],
        
        # Carga
        "cargo": Dict[str, int],         # {product_code: quantity}
        
        # Historial
        "events": List[Dict],
        "dice_rolls": List[Dict]
    }

Dependencias:
    - json: Serialización/deserialización
    - pathlib.Path: Manejo de rutas de archivos
    - datetime: Timestamps

Notas de implementación:
    - Persistencia: Estado guardado automáticamente en operaciones críticas
    - Thread Safety: No implementada (FastAPI maneja concurrencia)
    - Validación: Campos actualizados sin validación (manejar en endpoints)
    - Event Queue: Lista ordenada de eventos futuros
    - Coordinate System: 1-based para display, 0-based para cálculos internos
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


class GameState:
    """
    Maneja el estado del juego con persistencia en archivos JSON.
    
    Cada partida tiene su propio directorio en `data/games/{game_id}/` con un
    archivo `state.json` que contiene todo el estado persistente.
    
    El estado se guarda automáticamente después de operaciones críticas como
    actualizaciones, eventos, o descubrimientos.
    
    Attributes:
        GAMES_DIR: Directorio base donde se almacenan todas las partidas
        game_id: Identificador único de la partida
        game_dir: Path al directorio de esta partida
        state_file: Path al archivo state.json
        state: Diccionario con todo el estado del juego
    
    Mejores prácticas:
        - Usar update() para cambios múltiples
        - Registrar eventos importantes con add_event()
        - Siempre llamar save() después de modificar estado manualmente
        - Validar coordenadas antes de usar métodos de navegación
        - Mantener consistencia entre explored_quadrants y quadrant_planets
    """
    
    GAMES_DIR = "data/games"
    
    def __init__(self, game_id: str):
        """
        Inicializa el gestor de estado para una partida.
        
        Args:
            game_id: Identificador único de la partida
        """
        self.game_id = game_id
        self.game_dir = Path(self.GAMES_DIR) / game_id
        self.state_file = self.game_dir / "state.json"
        self.state = self._load_or_create_state()
    
    def _load_or_create_state(self) -> Dict[str, Any]:
        """
        Carga el estado existente o crea uno nuevo.
        
        Si existe un archivo state.json, lo carga. Si no existe, crea un
        estado por defecto con todos los campos inicializados.
        
        Returns:
            Diccionario con el estado del juego
        """
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Crear nuevo estado de juego
            return self._create_default_state()
    
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
            
            # Dificultad y Tesorería - Configurado durante setup
            "difficulty": None,  # "easy" (600 SC), "normal" (500 SC), "hard" (400 SC)
            "treasury": 0,  # Saldo en Créditos Spacegom (SC)
            "reputation": 0,  # Reputación inicial
            
            # Historial de Transacciones
            "transactions": [],  # [{date, amount, description, category}]
            
            # Nota: El personal se gestiona en la base de datos (tabla Personnel)
            # Los datos de la tripulación se consultan desde la BD, no se almacenan en el estado
            
            # Comercio - Carga actual
            "cargo": {},  # {product_code: quantity} - Productos en la bodega
            
            # Historial - Eventos y tiradas de dados
            "events": [],  # Lista de eventos del juego
            "dice_rolls": [],  # Historial de tiradas de dados
            
            # Flags de Acciones - Control de acciones disponibles
            "passenger_transport_available": True  # Reset al moverse entre cuadrantes
        }
    
    def save(self) -> None:
        """
        Guarda el estado actual en el archivo state.json con timestamp actualizado.
        
        Crea el directorio si no existe y actualiza el campo `updated_at` con
        la fecha y hora actual antes de guardar.
        """
        # Asegurar que el directorio existe
        self.game_dir.mkdir(parents=True, exist_ok=True)
        
        # Actualizar timestamp
        self.state["updated_at"] = datetime.now().isoformat()
        
        # Escribir a archivo
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
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
    
    def add_event(self, event_type: str, description: str, data: Optional[Dict] = None) -> None:
        """
        Agrega un evento al historial de eventos del juego.
        
        Los eventos se almacenan con timestamp, fecha del juego, tipo, descripción
        y datos adicionales opcionales. Se guarda automáticamente después de agregar.
        
        Args:
            event_type: Tipo de evento (ej: "hire", "trade", "mission")
            description: Descripción legible del evento
            data: Diccionario opcional con datos adicionales del evento
        """
        # Calcular fecha actual del juego
        year = self.state.get('year', 1)
        month = self.state.get('month', 1)
        day = self.state.get('day', 1)
        game_date = f"{day:02d}-{month:02d}-{year}"

        event = {
            "timestamp": datetime.now().isoformat(),
            "game_date": game_date,
            "type": event_type,
            "description": description,
            "data": data or {}
        }
        self.state["events"].append(event)
        self.save()
    
    def record_dice_roll(self, num_dice: int, results: list, is_manual: bool, purpose: str = "") -> Dict[str, Any]:
        """
        Registra una tirada de dados en el historial.
        
        Almacena información completa sobre la tirada para su posterior consulta.
        Se integra con el sistema de logging y se guarda automáticamente.
        
        Args:
            num_dice: Número de dados tirados
            results: Lista de resultados individuales de cada dado
            is_manual: True si fue tirada manual (dados físicos), False si fue automática
            purpose: Propósito o descripción de la tirada (para debugging)
        
        Returns:
            Diccionario con la información de la tirada registrada
        """
        roll = {
            "timestamp": datetime.now().isoformat(),
            "num_dice": num_dice,
            "results": results,
            "total": sum(results),
            "is_manual": is_manual,
            "purpose": purpose
        }
        self.state["dice_rolls"].append(roll)
        self.save()
        return roll
    
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
        """
        Lista todas las partidas disponibles con metadata básica.
        
        Recorre el directorio de juegos y carga información básica de cada
        partida guardada. Retorna una lista ordenada por fecha de actualización
        (más recientes primero).
        
        Returns:
            Lista de diccionarios con información básica de cada partida:
            - game_id: Identificador de la partida
            - created_at: Fecha de creación
            - updated_at: Última actualización
            - month: Mes actual del juego
            - credits: Créditos actuales (si existe)
        """
        games_path = Path(cls.GAMES_DIR)
        if not games_path.exists():
            return []
        
        games = []
        for game_dir in games_path.iterdir():
            if game_dir.is_dir():
                state_file = game_dir / "state.json"
                if state_file.exists():
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        games.append({
                            "game_id": game_dir.name,
                            "created_at": state.get("created_at"),
                            "updated_at": state.get("updated_at"),
                            "month": state.get("month", 1),
                            "credits": state.get("credits", 0)
                        })
        
        return sorted(games, key=lambda x: x["updated_at"], reverse=True)
    
    @classmethod
    def create_new_game(cls, game_name: Optional[str] = None) -> "GameState":
        """
        Crea una nueva partida con ID único.
        
        Si no se proporciona nombre, genera uno automáticamente basado en
        timestamp. Limpia el nombre para crear un ID válido (solo alfanuméricos,
        guiones y guiones bajos).
        
        Args:
            game_name: Nombre opcional para la partida
        
        Returns:
            Nueva instancia de GameState con estado inicializado
        
        Example:
            >>> game = GameState.create_new_game("Mi Partida")
            >>> game.game_id
            'mi_partida'
        """
        if not game_name:
            game_name = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Limpiar nombre del juego (remover caracteres inválidos)
        game_id = "".join(c for c in game_name if c.isalnum() or c in ('_', '-')).lower()
        
        return cls(game_id)
