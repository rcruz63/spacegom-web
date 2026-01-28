"""
Trade Manager for Spacegom
Handles logic for buying/selling, price calculation, and cooldowns.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import Planet, TradeOrder
from app.game_state import GameState
from app.dice import DiceRoller
from app.time_manager import GameCalendar
import math

# Trading Constants from Manual (Page 1)
# Code: {buy_price, sell_price, production_days, demand_days}
TRADE_PRODUCTS = {
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
    def __init__(self, game_id: str, db: Session):
        self.game_id = game_id
        self.db = db
        self.game_state = GameState(game_id)

    def get_market_data(self, planet_code: int) -> Dict:
        """
        Get available products to buy and demand for selling at current planet.
        Checks cooldowns based on previous TradeOrders.
        """
        planet = self.db.query(Planet).filter(Planet.code == planet_code).first()
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

            # Check cooldown
            # Find most recent buy of this product at this planet
            last_order = self.db.query(TradeOrder).filter(
                TradeOrder.game_id == self.game_id,
                TradeOrder.buy_planet_code == planet_code,
                TradeOrder.product_code == code
            ).order_by(TradeOrder.id.desc()).first()
            
            days_passed = 9999
            on_cooldown = False
            
            if last_order:
                # Calculate days passed since buy_date
                current_date_str = GameCalendar.date_to_string(
                    self.game_state.state.get("year", 1),
                    self.game_state.state.get("month", 1),
                    self.game_state.state.get("day", 1)
                )
                
                days_passed = GameCalendar.days_between(last_order.buy_date, current_date_str)
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
                "max_ucn": planet.ucn_per_order, # From Planet stats
                "cooldown": on_cooldown,
                "days_remaining": max(0, product_info["prod_days"] - days_passed) if last_order else 0
            })

        # --- SELL OPTIONS (What I have in cargo that I can sell) ---
        # Get active orders (in_transit)
        active_orders = self.db.query(TradeOrder).filter(
            TradeOrder.game_id == self.game_id,
            TradeOrder.status == "in_transit"
        ).all()
        
        # Calculate current date once
        current_date_str = GameCalendar.date_to_string(
            self.game_state.state.get("year", 1),
            self.game_state.state.get("month", 1),
            self.game_state.state.get("day", 1)
        )
        
        for order in active_orders:
            # Check if this planet buys this product (Demand)
            # Rule: Planets demand products they DON'T produce.
            is_produced_here = capabilities.get(order.product_code, False)
            if is_produced_here:
                continue

            # Check demand cooldown
            # Find most recent sell of this product at this planet
            last_sell = self.db.query(TradeOrder).filter(
                TradeOrder.game_id == self.game_id,
                TradeOrder.sell_planet_code == planet_code,
                TradeOrder.product_code == order.product_code,
                TradeOrder.status == "sold"
            ).order_by(TradeOrder.sell_date.desc()).first()
            
            can_sell = True
            days_remaining = 0
            
            product_info = TRADE_PRODUCTS.get(order.product_code, {})
            demand_days = product_info.get("demand_days", 30)
            
            if last_sell:
                # We need sell_date. If stored as string "DD-MM-YYYY", we parse it.
                # Assuming sell_date format matches GameCalendar
                if last_sell.sell_date:
                     days_passed = GameCalendar.days_between(last_sell.sell_date, current_date_str)
                     if days_passed < demand_days:
                         can_sell = False
                         days_remaining = demand_days - days_passed
            
            sell_options.append({
                "order_id": order.id,
                "product_code": order.product_code,
                "product_name": product_info.get("name", order.product_code),
                "quantity": order.quantity,
                "buy_price": order.total_buy_price,
                "base_sell_price_unit": product_info.get("sell", 0),
                "can_sell": can_sell,
                "days_remaining": days_remaining
            })
            
        return {
            "buy": buy_options,
            "sell": sell_options,
            "planet_ucn_limit": planet.ucn_per_order
        }

    def calculate_loading_time(self, total_ucn: int) -> int:
        """
        Calculate loading days based on Logistics Operators
        Rule: 
        - Roll 2d6 for each 'Operario de logística y almacén'
        - >= 7: 10 UCN/day
        - < 7: 5 UCN/day
        - If no operators: 5 UCN/day (Base rate)
        """
        from app.database import Personnel
        
        logistics_ops = self.db.query(Personnel).filter(
            Personnel.game_id == self.game_id,
            Personnel.position == "Operario de logística y almacén",
            Personnel.is_active == True
        ).all()
        
        daily_rate = 0
        dice_details = []
        
        if not logistics_ops:
            daily_rate = 5 # Base valid for non-specialists? A bit generous but enables play.
        else:
            for op in logistics_ops:
                # Roll 2d6
                roll = sum(DiceRoller.roll_dice(2))
                
                # Apply modifiers
                exp_mod = {"N": -1, "E": 0, "V": 1}.get(op.experience, 0)
                morale_mod = {"B": -1, "M": 0, "A": 1}.get(op.morale, 0)
                
                total = roll + exp_mod + morale_mod
                
                rate = 10 if total >= 7 else 5
                daily_rate += rate
                dice_details.append({"name": op.name, "roll": total, "rate": rate})
                
        days_needed = math.ceil(total_ucn / daily_rate)
        return days_needed

    def execute_batch_buy(self, items: List[Dict], planet_code: int) -> Dict:
        """
        Execute a batch of buy orders (Shopping Basket).
        Returns success, total cost, and loading time details.
        items: List of {"product_code": str, "quantity": int, "unit_price": int}
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
        
        # Obtener nombre del planeta una sola vez
        try:
            planet = self.db.query(Planet).filter(Planet.code == planet_code).first()
            planet_name = planet.name if planet else f"Planeta {planet_code}"
        except Exception as e:
            planet_name = f"Planeta {planet_code}"
        
        from app.event_logger import EventLogger
        
        # Timestamp para created_at y updated_at
        timestamp = datetime.now().isoformat()
        
        try:
            for item in items:
                # Deduct funds
                curr_cost = item["quantity"] * item["unit_price"]
                self.game_state.state["treasury"] -= curr_cost
                
                # Create Order
                new_order = TradeOrder(
                    game_id=self.game_id,
                    area=self.game_state.state.get("area", 0),
                    buy_planet_code=planet_code,
                    buy_planet_name=planet_name,
                    product_code=item["product_code"],
                    quantity=item["quantity"],
                    buy_price_per_unit=item["unit_price"],
                    total_buy_price=curr_cost,
                    buy_date=current_date_str,
                    traceability=True, # Default True
                    status="in_transit",
                    created_at=timestamp,
                    updated_at=timestamp
                )
                self.db.add(new_order)
                self.db.commit() # Commit to get ID
                created_orders.append(new_order.id)
                
                # Log Transaction
                self.game_state.state["transactions"].append({
                    "date": current_date_str,
                    "amount": -curr_cost,
                    "description": f"Compra {item['quantity']} UCN de {item['product_code']}",
                    "category": "Comercio"
                })
                
                # Update Cargo Cache
                if "cargo" not in self.game_state.state:
                    self.game_state.state["cargo"] = {}
                curr_c = self.game_state.state["cargo"].get(item["product_code"], 0)
                self.game_state.state["cargo"][item["product_code"]] = curr_c + item["quantity"]

            # Update Storage Global
            self.game_state.state["storage"] += total_ucn_all
            
            # 3. Calculate Loading Time
            loading_days = self.calculate_loading_time(total_ucn_all)
            
            # Log Event
            EventLogger._log_to_game(
                self.game_state,
                f"🛒 Compra Lote: {len(items)} productos, {total_ucn_all} UCN total. Coste: {total_cost_all} SC. Tiempo de carga: {loading_days} días.",
                "info"
            )
            
            self.game_state.save()
            
            return {
                "success": True, 
                "total_cost": total_cost_all,
                "loading_days": loading_days,
                "orders": created_orders
            }
        except Exception as e:
            # Rollback en caso de error
            self.db.rollback()
            # Revertir cambios en el estado del juego
            self.game_state.state["treasury"] = treasury
            self.game_state.state["storage"] = current_storage
            if "cargo" in self.game_state.state:
                # Revertir cargo también si es necesario
                pass
            self.game_state.save()
            return {"success": False, "error": f"Error al procesar la compra: {str(e)}"}

    def negotiate_price(self, negotiator_skill: int, reputation: int, is_buy: bool, manual_roll: Optional[int] = None) -> Dict:
        """
        Calculate price multiplier based on 2d6 roll
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

    def _get_game_date_value(self):
        # Helper to get numeric date value for diffs
        # Year * 12 * 35 + Month * 35 + Day
        state = self.game_state.state
        return (state.get("year", 1) * 420) + (state.get("month", 1) * 35) + state.get("day", 1)

    def execute_buy(self, planet_code: int, product_code: str, quantity: int, unit_price: int, traceability: bool = True) -> Dict:
        """
        Execute a buy order.
        1. Check treasury
        2. Deduct cost
        3. Create TradeOrder
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
            
        # Deduct Cost
        self.game_state.state["treasury"] -= total_cost
        self.game_state.update(treasury=self.game_state.state["treasury"])
        
        # Update Storage
        self.game_state.state["storage"] = current_storage + quantity
        
        # Obtener nombre del planeta
        planet = self.db.query(Planet).filter(Planet.code == planet_code).first()
        planet_name = planet.name if planet else f"Planeta {planet_code}"
        
        # Timestamp para created_at y updated_at
        timestamp = datetime.now().isoformat()
        
        # Create Trade Order
        new_order = TradeOrder(
            game_id=self.game_id,
            area=self.game_state.state.get("area", 0), # Fallback 0
            buy_planet_code=planet_code,
            buy_planet_name=planet_name,
            product_code=product_code,
            quantity=quantity,
            buy_price_per_unit=unit_price,
            total_buy_price=total_cost,
            buy_date=f"{self.game_state.state.get('day'):02d}-{self.game_state.state.get('month'):02d}-{self.game_state.state.get('year')}",
            traceability=traceability,
            status="in_transit",
            created_at=timestamp,
            updated_at=timestamp
        )
        self.db.add(new_order)
        self.db.commit()
        
        # Log Transaction
        game_date_str = GameCalendar.date_to_string(
            self.game_state.state.get("year", 1),
            self.game_state.state.get("month", 1),
            self.game_state.state.get("day", 1)
        )

        self.game_state.state["transactions"].append({
            "date": game_date_str,
            "amount": -total_cost,
            "description": f"Compra {quantity} UCN de {product_code}",
            "category": "Comercio"
        })
        
        # Log Event
        from app.event_logger import EventLogger
        EventLogger._log_to_game(
            self.game_state,
            f"🛒 Compra realizada: {quantity} UCN de {product_code} por {total_cost} SC",
            "info"
        )
        
        # Update Cargo State (for UI/JSON simplicity)
        if "cargo" not in self.game_state.state:
            self.game_state.state["cargo"] = {}
            
        current_qty = self.game_state.state["cargo"].get(product_code, 0)
        self.game_state.state["cargo"][product_code] = current_qty + quantity
        
        self.game_state.save()
        
        return {"success": True, "order_id": new_order.id, "balance": self.game_state.state["treasury"]}

    def execute_sell(self, order_id: int, planet_code: int, sell_price_total: int) -> Dict:
        """
        Execute a sell order.
        1. Update TradeOrder
        2. Add credits
        """
        order = self.db.query(TradeOrder).filter(TradeOrder.id == order_id).first()
        if not order:
            return {"success": False, "error": "Order not found"}
            
        if order.status == "sold":
             return {"success": False, "error": "Order already sold"}
        
        # Obtener nombre del planeta de venta
        planet = self.db.query(Planet).filter(Planet.code == planet_code).first()
        planet_name = planet.name if planet else f"Planeta {planet_code}"
             
        # Update Order
        order.sell_planet_code = planet_code
        order.sell_planet_name = planet_name
        order.sell_price_total = sell_price_total
        order.sell_date = f"{self.game_state.state.get('day'):02d}-{self.game_state.state.get('month'):02d}-{self.game_state.state.get('year')}"
        order.status = "sold"
        order.profit = sell_price_total - order.total_buy_price
        order.updated_at = datetime.now().isoformat()
        
        self.db.commit()
        
        # Add Credits
        self.game_state.state["treasury"] += sell_price_total
        self.game_state.update(treasury=self.game_state.state["treasury"])
        
        # Update Storage
        current_storage = self.game_state.state.get("storage", 0)
        self.game_state.state["storage"] = max(0, current_storage - order.quantity)
        
        # Log Transaction
        game_date_str = GameCalendar.date_to_string(
            self.game_state.state.get("year", 1),
            self.game_state.state.get("month", 1),
            self.game_state.state.get("day", 1)
        )

        self.game_state.state["transactions"].append({
            "date": game_date_str,
            "amount": sell_price_total,
            "description": f"Venta {order.quantity} UCN de {order.product_code}",
            "category": "Comercio"
        })
        
        # Log Event
        from app.event_logger import EventLogger
        EventLogger._log_to_game(
            self.game_state,
            f"💰 Venta realizada: {order.quantity} UCN de {order.product_code} por {sell_price_total} SC (Beneficio: {order.profit} SC)",
            "success"
        )
        
        # Update Cargo State
        if "cargo" in self.game_state.state and order.product_code in self.game_state.state["cargo"]:
            current_qty = self.game_state.state["cargo"][order.product_code]
            new_qty = max(0, current_qty - order.quantity)
            if new_qty == 0:
                del self.game_state.state["cargo"][order.product_code]
            else:
                self.game_state.state["cargo"][order.product_code] = new_qty
        
        self.game_state.save()
        
        return {"success": True, "profit": order.profit, "balance": self.game_state.state["treasury"]}

