"""
Módulo de gestión de comercio para Spacegom.

Maneja la lógica de compra/venta, cálculo de precios, negociación y cooldowns
de comercio según las reglas del manual del juego.

Dependencias:
    - app.planets_repo: get_planet_by_code
    - app.game_state: GameState
    - app.dice: DiceRoller
    - app.time_manager: GameCalendar
"""
from typing import Any, Dict, List, Optional, Tuple

from datetime import datetime

from app.planets_repo import get_planet_by_code
from app.game_state import GameState
from app.dice import DiceRoller
from app.time_manager import GameCalendar
import math

# Constantes de productos comerciales del manual (Página 1)
# Estructura: código_producto: {nombre, precio_compra, precio_venta, días_producción, días_demanda}
TRADE_PRODUCTS: Dict[str, Dict[str, Any]] = {
    "INDU": {"name": "Productos industriales", "buy": 9, "sell": 18, "prod_days": 30, "demand_days": 50},
    "BASI": {"name": "Materiales básicos", "buy": 11, "sell": 21, "prod_days": 40, "demand_days": 50},
    "ALIM": {"name": "Alimentos", "buy": 4, "sell": 11, "prod_days": 30, "demand_days": 40},
    "MADE": {"name": "Madera", "buy": 6, "sell": 17, "prod_days": 30, "demand_days": 50},
    "AGUA": {"name": "Agua potable", "buy": 2, "sell": 5, "prod_days": 20, "demand_days": 20},
    "MICO": {"name": "Minerales comunes", "buy": 5, "sell": 9, "prod_days": 30, "demand_days": 50},
    "MIRA": {"name": "Minerales raros", "buy": 13, "sell": 30, "prod_days": 50, "demand_days": 60},
    "MIPR": {"name": "Metales preciosos", "buy": 20, "sell": 60, "prod_days": 80, "demand_days": 80},
    "PAVA": {"name": "Productos avanzados", "buy": 15, "sell": 30, "prod_days": 40, "demand_days": 60},
    "A": {"name": "Armas (Espacial)", "buy": 7, "sell": 15, "prod_days": 40, "demand_days": 40},
    "AE": {"name": "Armas (Espacial+)", "buy": 10, "sell": 23, "prod_days": 60, "demand_days": 60},
    "AEI": {"name": "Armas (Interestelar)", "buy": 20, "sell": 45, "prod_days": 80, "demand_days": 80},
    "COM": {"name": "Combustible", "buy": 4, "sell": 7, "prod_days": 30, "demand_days": 20},
}

class TradeManager:
    """
    Gestor de comercio para una partida específica.
    
    Maneja todas las operaciones comerciales incluyendo:
    - Obtención de datos de mercado (productos disponibles para compra/venta)
    - Negociación de precios con tiradas de dados
    - Ejecución de órdenes de compra y venta
    - Cálculo de tiempos de carga según operarios de logística
    - Gestión de cooldowns basados en órdenes previas
    
    Attributes:
        game_id: Identificador de la partida
        db: Sesión de base de datos SQLAlchemy
        game_state: Instancia de GameState para la partida
    """
    
    def __init__(self, game_id: str):
        """Inicializa el gestor de comercio para una partida (usa GameState/DynamoDB)."""
        self.game_id = game_id
        self.game_state = GameState(game_id)

    def get_market_data(self, planet_code: int) -> Dict:
        """
        Obtiene productos disponibles para comprar/vender en un planeta.
        
        Considera las capacidades de producción del planeta y los cooldowns
        basados en órdenes comerciales previas. Los productos disponibles para
        compra son aquellos que el planeta produce. Los productos disponibles
        para venta son aquellos que el planeta NO produce (demanda).
        
        Args:
            planet_code: Código del planeta (111-666)
        
        Returns:
            Diccionario con:
            {
                "buy": List[Dict],  # Productos disponibles para compra
                "sell": List[Dict], # Órdenes disponibles para venta
                "planet_ucn_limit": int  # Límite UCN por orden del planeta
            }
            
            Cada producto de compra incluye:
            - code, name, base_price, base_sell, base_profit
            - prod_days, demand_days, max_ucn
            - cooldown (bool), days_remaining
            
            Cada orden de venta incluye:
            - order_id, product_code, product_name, quantity
            - buy_price, base_sell_price_unit
            - can_sell (bool), days_remaining
        """
        planet = get_planet_by_code(planet_code)
        if not planet:
            return {}
            
        # 1. Get Planet Production Capabilities (Booleans)
        capabilities = {
            "INDU": planet.product_indu,
            "BASI": planet.product_basi,
            "ALIM": planet.product_alim,
            "MADE": planet.product_made,
            "AGUA": planet.product_agua,
            "MICO": planet.product_mico,
            "MIRA": planet.product_mira,
            "MIPR": planet.product_mipr,
            "PAVA": planet.product_pava,
            "A": planet.product_a,
            "AE": planet.product_ae,
            "AEI": planet.product_aei,
            "COM": planet.product_com
        }
        
        # 2. Check Orders for Cooldowns
        # Get orders for this planet
        # We need "last_buy_date" and "last_sell_date" for each product on this planet
        # Logic: Find orders where buy_planet_code == planet_code
        
        buy_options = []
        sell_options = []
        
        # Determine current game date (simplified: total days)
        current_date_val = self._get_game_date_value()
        
        # --- BUY OPTIONS (What I can buy here) ---
        for code, can_produce in capabilities.items():
            if not can_produce:
                continue
                
            product_info = TRADE_PRODUCTS.get(code, {})
            if not product_info:
                continue

            orders = [o for o in self.game_state.get_trade_orders()
                      if o.get("buy_planet_code") == planet_code and o.get("product_code") == code]
            orders.sort(key=lambda o: o.get("id", 0), reverse=True)
            last_order = orders[0] if orders else None

            days_passed = 9999
            on_cooldown = False
            if last_order:
                current_date_str = GameCalendar.date_to_string(
                    self.game_state.state.get("year", 1),
                    self.game_state.state.get("month", 1),
                    self.game_state.state.get("day", 1),
                )
                days_passed = GameCalendar.days_between(last_order.get("buy_date", ""), current_date_str)
                prod_days = product_info["prod_days"]
                if days_passed < prod_days:
                    on_cooldown = True

            buy_options.append({
                "code": code,
                "name": product_info["name"],
                "base_price": product_info["buy"],
                "base_sell": product_info["sell"],
                "base_profit": product_info["sell"] - product_info["buy"],
                "prod_days": product_info["prod_days"],
                "demand_days": product_info["demand_days"],
                "max_ucn": planet.ucn_per_order,
                "cooldown": on_cooldown,
                "days_remaining": max(0, product_info["prod_days"] - days_passed) if last_order else 0,
            })

        active_orders = [o for o in self.game_state.get_trade_orders() if o.get("status") == "in_transit"]
        current_date_str = GameCalendar.date_to_string(
            self.game_state.state.get("year", 1),
            self.game_state.state.get("month", 1),
            self.game_state.state.get("day", 1),
        )

        for order in active_orders:
            is_produced_here = capabilities.get(order.get("product_code"), False)
            if is_produced_here:
                continue

            sold = [o for o in self.game_state.get_trade_orders()
                    if o.get("sell_planet_code") == planet_code
                    and o.get("product_code") == order.get("product_code")
                    and o.get("status") == "sold"]
            sold.sort(key=lambda o: o.get("sell_date", ""), reverse=True)
            last_sell = sold[0] if sold else None

            can_sell = True
            days_remaining = 0
            product_info = TRADE_PRODUCTS.get(order.get("product_code"), {})
            demand_days = product_info.get("demand_days", 30)
            if last_sell and last_sell.get("sell_date"):
                days_passed = GameCalendar.days_between(last_sell["sell_date"], current_date_str)
                if days_passed < demand_days:
                    can_sell = False
                    days_remaining = demand_days - days_passed

            sell_options.append({
                "order_id": order["id"],
                "product_code": order["product_code"],
                "product_name": product_info.get("name", order.get("product_code", "")),
                "quantity": order["quantity"],
                "buy_price": order["total_buy_price"],
                "base_sell_price_unit": product_info.get("sell", 0),
                "can_sell": can_sell,
                "days_remaining": days_remaining,
            })
            
        return {
            "buy": buy_options,
            "sell": sell_options,
            "planet_ucn_limit": planet.ucn_per_order
        }

    def calculate_loading_time(self, total_ucn: int) -> int:
        """
        Calcula días de carga basado en Operarios de logística y almacén.
        
        Reglas:
        - Por cada operario: tirar 2d6
        - Resultado >= 7: 10 UCN/día por operario
        - Resultado < 7: 5 UCN/día por operario
        - Sin operarios: 5 UCN/día (tasa base)
        
        Los modificadores de experiencia y moral se aplican a la tirada:
        - Experiencia: Novato (-1), Estándar (0), Veterano (+1)
        - Moral: Baja (-1), Media (0), Alta (+1)
        
        Args:
            total_ucn: Total de UCN a cargar
        
        Returns:
            Días necesarios para completar la carga (mínimo 1 día)
        """
        logistics_ops = [p for p in self.game_state.get_personnel(active_only=True)
                        if p.get("position") == "Operario de logística y almacén"]
        daily_rate = 0
        dice_details = []

        if not logistics_ops:
            daily_rate = 5
        else:
            for op in logistics_ops:
                roll = sum(DiceRoller.roll_dice(2))
                exp_mod = {"N": -1, "E": 0, "V": 1}.get(op.get("experience", "N"), 0)
                morale_mod = {"B": -1, "M": 0, "A": 1}.get(op.get("morale", "M"), 0)
                total = roll + exp_mod + morale_mod
                rate = 10 if total >= 7 else 5
                daily_rate += rate
                dice_details.append({"name": op.get("name"), "roll": total, "rate": rate})
                
        days_needed = math.ceil(total_ucn / daily_rate)
        return days_needed

    def execute_batch_buy(self, items: List[Dict], planet_code: int) -> Dict:
        """
        Ejecuta un lote de órdenes de compra (cesta de compra).
        
        Valida todas las compras antes de ejecutar ninguna, asegurando que
        hay fondos y capacidad suficientes para todo el lote. Si alguna validación
        falla, no se ejecuta ninguna compra.
        
        Args:
            items: Lista de items a comprar, cada uno con:
                  {"product_code": str, "quantity": int, "unit_price": int}
            planet_code: Código del planeta donde se compra (111-666)
        
        Returns:
            Diccionario con:
            {
                "success": bool,           # True si todas las compras fueron exitosas
                "total_cost": int,         # Coste total del lote
                "loading_days": int,       # Días necesarios para cargar
                "orders": List[int],       # IDs de órdenes creadas
                "error": str               # Mensaje de error (si !success)
            }
        """
        total_cost_all = 0
        total_ucn_all = 0
        
        # 1. Validate ALL items first
        current_storage = self.game_state.state.get("storage", 0)
        max_storage = self.game_state.state.get("storage_max", 40)
        treasury = self.game_state.state.get("treasury", 0)
        
        for item in items:
            qty = item["quantity"]
            price = item["unit_price"]
            total_ucn_all += qty
            total_cost_all += (qty * price)
            
        if current_storage + total_ucn_all > max_storage:
             return {"success": False, "error": f"Capacidad insuficiente para el lote completo. Espacio: {max_storage - current_storage} UCN"}
             
        if treasury < total_cost_all:
             return {"success": False, "error": f"Fondos insuficientes. Coste total: {total_cost_all} SC"}
             
        # 2. Execute Each Order
        created_orders = []
        current_date_str = GameCalendar.date_to_string(
            self.game_state.state.get("year", 1),
            self.game_state.state.get("month", 1),
            self.game_state.state.get("day", 1)
        )
        
        try:
            planet = get_planet_by_code(planet_code)
            planet_name = planet.name if planet else f"Planeta {planet_code}"
        except Exception:
            planet_name = f"Planeta {planet_code}"
        
        from app.event_logger import EventLogger

        timestamp = datetime.now().isoformat()
        try:
            for item in items:
                curr_cost = item["quantity"] * item["unit_price"]
                self.game_state.state["treasury"] -= curr_cost

                oid = self.game_state.add_trade_order({
                    "area": self.game_state.state.get("area", 0),
                    "buy_planet_code": planet_code,
                    "buy_planet_name": planet_name,
                    "product_code": item["product_code"],
                    "quantity": item["quantity"],
                    "buy_price_per_unit": item["unit_price"],
                    "total_buy_price": curr_cost,
                    "buy_date": current_date_str,
                    "traceability": True,
                    "status": "in_transit",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                })
                created_orders.append(oid)

                self.game_state.append_transaction({
                    "date": current_date_str,
                    "amount": -curr_cost,
                    "description": f"Compra {item['quantity']} UCN de {item['product_code']}",
                    "category": "Comercio",
                })

                self.game_state.state.setdefault("cargo", {})
                curr_c = self.game_state.state["cargo"].get(item["product_code"], 0)
                self.game_state.state["cargo"][item["product_code"]] = curr_c + item["quantity"]

            self.game_state.state["storage"] = self.game_state.state.get("storage", 0) + total_ucn_all
            loading_days = self.calculate_loading_time(total_ucn_all)

            EventLogger._log_to_game(
                self.game_state,
                f"🛒 Compra Lote: {len(items)} productos, {total_ucn_all} UCN total. Coste: {total_cost_all} SC. Tiempo de carga: {loading_days} días.",
                "info",
            )
            self.game_state.save()

            return {"success": True, "total_cost": total_cost_all, "loading_days": loading_days, "orders": created_orders}
        except Exception as e:
            self.game_state.state["treasury"] = treasury
            self.game_state.state["storage"] = current_storage
            self.game_state.save()
            return {"success": False, "error": f"Error al procesar la compra: {str(e)}"}

    def negotiate_price(self, negotiator_skill: int, reputation: int, is_buy: bool, manual_roll: Optional[int] = None) -> Dict:
        """
        Calcula multiplicador de precio basado en tirada de 2d6.
        
        La negociación determina el precio final de compra/venta:
        - Resultado < 7: Malo (1.2x compra, 0.8x venta) + pérdida de moral
        - Resultado 7-9: Normal (1.0x) sin efectos
        - Resultado >= 10: Bueno (0.8x compra, 1.2x venta) + ganancia de moral
        
        Modificadores aplicados:
        - Reputación: Reputación / 2 (redondeo hacia abajo)
        - Habilidad del negociador: Según nivel de experiencia y moral
        
        Las negociaciones consumen tiempo:
        - Compra: 1 día por producto
        - Venta: 1d6 días
        
        Args:
            negotiator_skill: Habilidad del negociador (modificador de skill)
            reputation: Reputación actual de la compañía
            is_buy: True si es compra, False si es venta
            manual_roll: Opcional resultado manual de tirada (dados físicos)
        
        Returns:
            Diccionario con:
            {
                "roll": int,              # Suma de los dados
                "dice": List[int],        # Valores individuales de dados
                "modifiers": Dict,        # Modificadores aplicados
                "total": int,             # Resultado final con modificadores
                "multiplier": float,      # Multiplicador de precio (0.8, 1.0, 1.2)
                "moral_effect": str,      # "Loss", "None", "Gain"
                "is_manual": bool,        # True si fue tirada manual
                "days_consumed": int      # Días consumidos por la negociación
            }
        """
        if manual_roll:
            roll = manual_roll
            dice = [] # Unknown split
            is_manual = True
        else:
            dice = DiceRoller.roll_dice(2)
            roll = sum(dice)
            is_manual = False
            
        # Modifiers
        # Reputation / 2 (round down)
        rep_mod = reputation // 2
        
        # Negotiator Skill (Simple mapping for now, should come from Employee object)
        skill_mod = 0 
        # Example: Novice=0, Expert=+1, Veteran=+2? Need to check rules.
        # Manual says: "aplica sus modificadores según su nivel de experiencia y moral"
        
        total = roll + rep_mod + skill_mod
        
        multiplier = 1.0
        moral_effect = "None"
        
        if total < 7:
            # FAIL
            multiplier = 1.2 if is_buy else 0.8
            moral_effect = "Loss"
        elif 7 <= total <= 9:
            # NORMAL
            multiplier = 1.0
            moral_effect = "None"
        else: # >= 10
            # SUCCESS
            multiplier = 0.8 if is_buy else 1.2
            moral_effect = "Gain"
            
        if is_buy:
            days_consumed = 1
        else:
            # 1D6 for selling
            days_consumed = DiceRoller.roll_dice(1)[0]
            
        return {
            "roll": roll,
            "dice": dice,
            "modifiers": {"reputation": rep_mod, "skill": skill_mod},
            "total": total,
            "multiplier": multiplier,
            "moral_effect": moral_effect,
            "is_manual": is_manual,
            "days_consumed": days_consumed
        }

    def _get_game_date_value(self) -> int:
        """
        Helper para obtener valor numérico de fecha del juego.
        
        Convierte la fecha del juego a un número entero para facilitar
        cálculos de diferencias de días. Usa el sistema de calendario
        personalizado (35 días/mes, 12 meses/año).
        
        Returns:
            Valor numérico: (año * 420) + (mes * 35) + día
        """
        state = self.game_state.state
        return (state.get("year", 1) * 420) + (state.get("month", 1) * 35) + state.get("day", 1)

    def execute_buy(self, planet_code: int, product_code: str, quantity: int, unit_price: int, traceability: bool = True) -> Dict:
        """
        Ejecuta una orden de compra.
        
        Proceso:
        1. Verifica tesorería suficiente
        2. Verifica capacidad de almacenamiento
        3. Descuenta costo de tesorería
        4. Crea TradeOrder en estado "in_transit"
        5. Actualiza almacenamiento y cargo
        6. Registra transacción y evento
        
        Args:
            planet_code: Código del planeta donde se compra (111-666)
            product_code: Código del producto (ej: "INDU", "BASI")
            quantity: Cantidad en UCN a comprar
            unit_price: Precio unitario negociado
            traceability: Si el producto tiene trazabilidad (default: True)
        
        Returns:
            Diccionario con:
            {
                "success": bool,      # True si la compra fue exitosa
                "order_id": int,      # ID de la orden creada (si success)
                "balance": int,       # Saldo restante en tesorería
                "error": str          # Mensaje de error (si !success)
            }
        """
        total_cost = quantity * unit_price
        
        # Check Storage Capacity
        current_storage = self.game_state.state.get("storage", 0)
        max_storage = self.game_state.state.get("storage_max", 40)
        
        if current_storage + quantity > max_storage:
            return {"success": False, "error": f"Capacidad insuficiente. Espacio: {max_storage - current_storage} UCN"}

        # Check Treasury
        if self.game_state.state.get("treasury", 0) < total_cost:
            return {"success": False, "error": "Fondos insuficientes"}
            
        self.game_state.state["treasury"] -= total_cost
        self.game_state.state["storage"] = current_storage + quantity

        planet = get_planet_by_code(planet_code)
        planet_name = planet.name if planet else f"Planeta {planet_code}"
        timestamp = datetime.now().isoformat()
        game_date_str = GameCalendar.date_to_string(
            self.game_state.state.get("year", 1),
            self.game_state.state.get("month", 1),
            self.game_state.state.get("day", 1),
        )

        order_id = self.game_state.add_trade_order({
            "area": self.game_state.state.get("area", 0),
            "buy_planet_code": planet_code,
            "buy_planet_name": planet_name,
            "product_code": product_code,
            "quantity": quantity,
            "buy_price_per_unit": unit_price,
            "total_buy_price": total_cost,
            "buy_date": game_date_str,
            "traceability": traceability,
            "status": "in_transit",
            "created_at": timestamp,
            "updated_at": timestamp,
        })
        self.game_state.append_transaction({
            "date": game_date_str,
            "amount": -total_cost,
            "description": f"Compra {quantity} UCN de {product_code}",
            "category": "Comercio",
        })

        from app.event_logger import EventLogger
        EventLogger._log_to_game(
            self.game_state,
            f"🛒 Compra realizada: {quantity} UCN de {product_code} por {total_cost} SC",
            "info",
        )

        self.game_state.state.setdefault("cargo", {})
        current_qty = self.game_state.state["cargo"].get(product_code, 0)
        self.game_state.state["cargo"][product_code] = current_qty + quantity
        self.game_state.save()

        return {"success": True, "order_id": order_id, "balance": self.game_state.state["treasury"]}

    def execute_sell(self, order_id: int, planet_code: int, sell_price_total: int) -> Dict:
        """
        Ejecuta una orden de venta.
        
        Proceso:
        1. Actualiza TradeOrder con datos de venta
        2. Cambia estado a "sold"
        3. Calcula ganancia (precio_venta - precio_compra)
        4. Agrega créditos a tesorería
        5. Actualiza almacenamiento y cargo
        6. Registra transacción y evento
        
        Args:
            order_id: ID de la TradeOrder a vender
            planet_code: Código del planeta donde se vende (111-666)
            sell_price_total: Precio total de venta negociado
        
        Returns:
            Diccionario con:
            {
                "success": bool,      # True si la venta fue exitosa
                "profit": int,        # Ganancia obtenida (si success)
                "balance": int,       # Saldo actualizado en tesorería
                "error": str          # Mensaje de error (si !success)
            }
        """
        order = self.game_state.get_order_by_id(order_id)
        if not order:
            return {"success": False, "error": "Order not found"}
        if order.get("status") == "sold":
            return {"success": False, "error": "Order already sold"}

        planet = get_planet_by_code(planet_code)
        planet_name = planet.name if planet else f"Planeta {planet_code}"
        game_date_str = GameCalendar.date_to_string(
            self.game_state.state.get("year", 1),
            self.game_state.state.get("month", 1),
            self.game_state.state.get("day", 1),
        )
        profit = sell_price_total - order["total_buy_price"]

        self.game_state.update_order(order_id, {
            "sell_planet_code": planet_code,
            "sell_planet_name": planet_name,
            "sell_price_total": sell_price_total,
            "sell_date": game_date_str,
            "status": "sold",
            "profit": profit,
            "updated_at": datetime.now().isoformat(),
        })

        self.game_state.state["treasury"] = self.game_state.state.get("treasury", 0) + sell_price_total
        current_storage = self.game_state.state.get("storage", 0)
        self.game_state.state["storage"] = max(0, current_storage - order["quantity"])

        self.game_state.append_transaction({
            "date": game_date_str,
            "amount": sell_price_total,
            "description": f"Venta {order['quantity']} UCN de {order['product_code']}",
            "category": "Comercio",
        })

        from app.event_logger import EventLogger
        EventLogger._log_to_game(
            self.game_state,
            f"💰 Venta realizada: {order['quantity']} UCN de {order['product_code']} por {sell_price_total} SC (Beneficio: {profit} SC)",
            "success",
        )

        cargo = self.game_state.state.get("cargo", {})
        if order["product_code"] in cargo:
            new_qty = max(0, cargo[order["product_code"]] - order["quantity"])
            if new_qty == 0:
                del self.game_state.state["cargo"][order["product_code"]]
            else:
                self.game_state.state["cargo"][order["product_code"]] = new_qty

        self.game_state.save()
        return {"success": True, "profit": profit, "balance": self.game_state.state["treasury"]}

