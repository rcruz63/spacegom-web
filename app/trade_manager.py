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
                # Assuming buy_date is saved as "YYYY-MM-DD" or similar, need parsing or storing simpler
                # For now assuming simple string comparison isn't enough, we need game logic
                # Let's rely on a helper to parse date if needed, or assume last_order is old enough for MVP
                # TODO: Implement precise date diff
                pass 
            
            buy_options.append({
                "code": code,
                "name": product_info["name"],
                "base_price": product_info["buy"],
                "base_sell": product_info["sell"],
                "base_profit": product_info["sell"] - product_info["buy"],
                "prod_days": product_info["prod_days"],
                "demand_days": product_info["demand_days"],
                "max_ucn": planet.ucn_per_order, # From Planet stats
                "cooldown": on_cooldown
            })

        # --- SELL OPTIONS (What I have in cargo that I can sell) ---
        # Get active orders (in_transit)
        active_orders = self.db.query(TradeOrder).filter(
            TradeOrder.game_id == self.game_id,
            TradeOrder.status == "in_transit"
        ).all()
        
        for order in active_orders:
            # Check if this planet buys this product (Demand)
            # Rule: Planets demand products they DON'T produce.
            # Manual: "Estos códigos son los que no hayas marcado con 'X'..." (Available to SELL = NOT Produced)
            
            is_produced_here = capabilities.get(order.product_code, False)
            if is_produced_here:
                continue

            # Check demand cooldown
            # Find most recent sell of this product at this planet
            # last_sell = ...
            
            product_info = TRADE_PRODUCTS.get(order.product_code, {})
            
            sell_options.append({
                "order_id": order.id,
                "product_code": order.product_code,
                "product_name": product_info.get("name", order.product_code),
                "quantity": order.quantity,
                "buy_price": order.total_buy_price,
                "base_sell_price_unit": product_info.get("sell", 0),
                "can_sell": True # Logic for cooldown here
            })
            
        return {
            "buy": buy_options,
            "sell": sell_options,
            "planet_ucn_limit": planet.ucn_per_order
        }

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
            
        return {
            "roll": roll,
            "dice": dice,
            "modifiers": {"reputation": rep_mod, "skill": skill_mod},
            "total": total,
            "multiplier": multiplier,
            "moral_effect": moral_effect,
            "is_manual": is_manual
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
        4. Create Cargo Loading Event (not implemented fully here, but placeholder)
        """
        total_cost = quantity * unit_price
        
        # Check Treasury
        if self.game_state.state.get("treasury", 0) < total_cost:
            return {"success": False, "error": "Insufficient funds"}
            
        # Deduct Cost
        self.game_state.state["treasury"] -= total_cost
        self.game_state.update(treasury=self.game_state.state["treasury"])
        
        # Create Trade Order
        new_order = TradeOrder(
            game_id=self.game_id,
            area=self.game_state.state.get("area", 0), # Fallback 0
            buy_planet_code=planet_code,
            buy_planet_name="", # TODO: Fetch name
            product_code=product_code,
            quantity=quantity,
            buy_price_per_unit=unit_price,
            total_buy_price=total_cost,
            buy_date=f"{self.game_state.state.get('day'):02d}-{self.game_state.state.get('month'):02d}-{self.game_state.state.get('year')}",
            traceability=traceability,
            status="in_transit"
        )
        self.db.add(new_order)
        self.db.commit()
        
        # Log Transaction
        self.game_state.state["transactions"].append({
            "date": datetime.now().isoformat(),
            "amount": -total_cost,
            "description": f"Compra {quantity} UCN de {product_code}",
            "category": "Comercio"
        })
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
             
        # Update Order
        order.sell_planet_code = planet_code
        order.sell_price_total = sell_price_total
        order.sell_planet_code = planet_code
        order.sell_price_total = sell_price_total
        order.sell_date = f"{self.game_state.state.get('day'):02d}-{self.game_state.state.get('month'):02d}-{self.game_state.state.get('year')}"
        order.status = "sold"
        order.profit = sell_price_total - order.total_buy_price
        
        self.db.commit()
        
        # Add Credits
        self.game_state.state["treasury"] += sell_price_total
        self.game_state.update(treasury=self.game_state.state["treasury"])
        
        # Log Transaction
        self.game_state.state["transactions"].append({
            "date": datetime.now().isoformat(),
            "amount": sell_price_total,
            "description": f"Venta {order.quantity} UCN de {order.product_code}",
            "category": "Comercio"
        })
        self.game_state.save()
        
        return {"success": True, "profit": order.profit, "balance": self.game_state.state["treasury"]}

