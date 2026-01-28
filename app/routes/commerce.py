"""
Routes para tesorería, comercio y transporte de pasajeros.

Este módulo contiene los endpoints relacionados con:
- Tesorería (balance, transacciones)
- Comercio (compra/venta de productos)
- Transporte de pasajeros
"""
from fastapi import APIRouter, Form, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import math

from app.database import get_db, Planet, Personnel, TradeOrder
from app.game_state import GameState
from app.dice import DiceRoller
from app.time_manager import GameCalendar

router = APIRouter(tags=["commerce"])


# ===== HELPER FUNCTIONS =====

def advance_game_time(game: GameState, days: int) -> str:
    """
    Avanza el tiempo del juego N días, manejando el cambio de calendario.
    
    Args:
        game: Instancia de GameState del juego
        days: Número de días a avanzar
        
    Returns:
        Nueva fecha en formato string (DD-MM-YYYY)
    """
    if days <= 0:
        return GameCalendar.date_to_string(
            game.state.get("year", 1),
            game.state.get("month", 1),
            game.state.get("day", 1)
        )
        
    current_date = GameCalendar.date_to_string(
        game.state.get("year", 1),
        game.state.get("month", 1),
        game.state.get("day", 1)
    )
    
    # Avance directo simple según el manual paso a paso
    # Idealmente se haría día a día si tuviéramos eventos granulares
    # Por ahora, simplemente saltamos.
    # TODO: Implementar bucle robusto de eventos día a día si es necesario.
    new_date_str = GameCalendar.add_days(current_date, days)
    y, m, d = GameCalendar.parse_date(new_date_str)
    
    game.state["year"] = y
    game.state["month"] = m
    game.state["day"] = d
    
    game.save()
    return new_date_str


# ===== TREASURY API =====

@router.get("/api/games/{game_id}/treasury")
async def get_treasury(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener información de la tesorería.

    Devuelve saldo actual, dificultad, reputación y transacciones recientes.
    """
    game = GameState(game_id)
    
    # Calculate monthly salaries from personnel
    personnel = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.is_active == True
    ).all()
    total_salaries = sum(p.monthly_salary for p in personnel)
    
    return {
        "current_balance": game.state.get("treasury", 0),
        "difficulty": game.state.get("difficulty"),
        "reputation": game.state.get("reputation", 0),
        "monthly_expenses": {
            "salaries": total_salaries,
            "loans": 0,  # TODO: implement loans system
            "total": total_salaries
        },
        "recent_transactions": game.state.get("transactions", [])[-10:]
    }


@router.post("/api/games/{game_id}/treasury/transaction")
async def add_transaction(
    game_id: str,
    amount: int = Form(...),
    description: str = Form(...),
    category: str = Form("other"),
) -> Dict[str, Any]:
    """Añadir una transacción a la tesorería."""
    game = GameState(game_id)
    
    transaction = {
        "date": datetime.now().isoformat(),
        "amount": amount,
        "description": description,
        "category": category
    }
    
    # Add transaction to history
    if "transactions" not in game.state:
        game.state["transactions"] = []
    game.state["transactions"].append(transaction)
    
    # Update treasury balance
    game.state["treasury"] = game.state.get("treasury", 0) + amount
    
    game.save()
    
    return {
        "status": "success",
        "new_balance": game.state["treasury"],
        "transaction": transaction
    }


# ===== PASSENGER TRANSPORT API =====

@router.get("/api/games/{game_id}/passenger-transport/info")
async def get_passenger_transport_info(
    game_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get info for passenger transport action.
    Returns capacity, current passengers, and modifiers.
    """
    from app.ship_data import get_ship_stats
    
    game = GameState(game_id)
    ship_stats = get_ship_stats(game.state.get("ship_model", "Basic Starfall"))
    
    # 1. Ship Capacity
    ship_capacity = ship_stats.get("passengers", 10)
    current_passengers = game.state.get("passengers", 0)
    
    # 2. Planet Info (Average Passengers)
    planet_code = game.state.get("current_planet_code")
    avg_passengers = 0
    if planet_code:
        planet = db.query(Planet).filter(Planet.code == planet_code).first()
        if planet:
            avg_passengers = planet.max_passengers
            
    # 3. Check for modifiers (Personnel)
    manager = db.query(Personnel).filter(
        Personnel.game_id == game_id, 
        Personnel.position == "Responsable de soporte a pasajeros",
        Personnel.is_active == True
    ).first()
    
    manager_bonus = 0
    if manager:
        exp_mod = {"N": -1, "E": 0, "V": 1}.get(manager.experience, 0)
        morale_mod = {"B": -1, "M": 0, "A": 1}.get(manager.morale, 0)
        rep_mod = math.floor(game.state.get("reputation", 0) / 2)
        
        manager_bonus = exp_mod + morale_mod + rep_mod
        
    # Flight Attendants
    flight_attendants = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.position == "Auxiliar de vuelo",
        Personnel.is_active == True
    ).all()
    
    attendants_count = len(flight_attendants)
    
    return {
        "ship_capacity": ship_capacity,
        "current_passengers": current_passengers,
        "planet_avg_passengers": avg_passengers,
        "modifiers": {
            "has_manager": manager is not None,
            "manager_name": manager.name if manager else None,
            "manager_bonus": manager_bonus,
            "attendants_count": attendants_count
        },
        "location": game.state.get("ship_location_on_planet", "Mundo"),
        "available": game.state.get("passenger_transport_available", True)
    }


@router.post("/api/games/{game_id}/passenger-transport/execute")
async def execute_passenger_transport(
    game_id: str,
    manual_dice: Optional[str] = Form(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute passenger transport action.
    
    1. Roll 2d6 (+ modifiers from Manager)
    2. Determine outcome (<7, 7-9, 10-12) -> Number of passengers
    3. Update Manager stats (Moral/XP) via personnel_manager
    4. Calculate Revenue (Base x Attendants multiplier + Attendants XP bonus)
    5. Update Game State (Treasury, Passengers)
    """
    from app.personnel_manager import update_employee_roll_stats
    from app.ship_data import get_ship_stats
    from app.event_logger import EventLogger
    
    game = GameState(game_id)
    
    # --- 1. Basic Checks ---
    if not game.state.get("passenger_transport_available", True):
        raise HTTPException(400, "Transporte de pasajeros ya realizado en esta visita. Debes viajar a otro cuadrante y volver.")

    planet_code = game.state.get("current_planet_code")
    planet = db.query(Planet).filter(Planet.code == planet_code).first()
    if not planet:
        raise HTTPException(400, "Not on a known planet")
        
    avg_passengers = planet.max_passengers
    ship_stats = get_ship_stats(game.state.get("ship_model", "Basic Starfall"))
    ship_capacity = ship_stats.get("passengers", 10)
    
    # --- 2. Calculate Modifiers ---
    manager = db.query(Personnel).filter(
        Personnel.game_id == game_id, 
        Personnel.position == "Responsable de soporte a pasajeros",
        Personnel.is_active == True
    ).first()
    
    total_mod = 0
    mods_detail = {}
    
    if manager:
        exp_mod = {"N": -1, "E": 0, "V": 1}.get(manager.experience, 0)
        morale_mod = {"B": -1, "M": 0, "A": 1}.get(manager.morale, 0)
        rep_mod = math.floor(game.state.get("reputation", 0) / 2)
        
        total_mod = exp_mod + morale_mod + rep_mod
        mods_detail = {"experience": exp_mod, "morale": morale_mod, "reputation_half": rep_mod}
    
    # --- 3. Roll Dice ---
    if manual_dice and manual_dice.strip():
        dice_values = [int(x.strip()) for x in manual_dice.split(",")]
        is_manual = True
    else:
        dice_values = DiceRoller.roll_dice(2, 6)
        is_manual = False
        
    dice_sum = sum(dice_values)
    final_result = dice_sum + total_mod
    
    # --- 4. Determine Passengers Boarded ---
    if final_result < 7:
        raw_passengers = math.floor(avg_passengers / 2)
        outcome_type = "low"
    elif final_result <= 9:
        raw_passengers = avg_passengers
        outcome_type = "mid"
    else:
        raw_passengers = avg_passengers * 2
        outcome_type = "high"
        
    # Cap at ship capacity
    boarding_passengers = min(int(raw_passengers), ship_capacity)
    
    # --- 5. Update Personnel Stats (Manager) ---
    personnel_changes = None
    if manager:
        personnel_changes = update_employee_roll_stats(manager, dice_values, final_result)
        # Log personnel changes
        for msg in personnel_changes["messages"]:
            EventLogger._log_to_game(game, f"👔 {manager.name}: {msg}", "info")
            
    # --- 6. Calculate Revenue ---
    flight_attendants = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.position == "Auxiliar de vuelo",
        Personnel.is_active == True
    ).all()
    
    num_aux = len(flight_attendants)
    if num_aux >= 3:
        multiplier = 4
    elif num_aux == 2:
        multiplier = 3
    elif num_aux == 1:
        multiplier = 2
    else:
        multiplier = 1
        
    base_revenue = boarding_passengers * multiplier
    
    # Adjustments: -5 per Novice Aux, +5 per Veteran Aux
    novice_penalty = sum(5 for a in flight_attendants if a.experience == "N")
    veteran_bonus = sum(5 for a in flight_attendants if a.experience == "V")
    
    final_revenue = base_revenue - novice_penalty + veteran_bonus
    final_revenue = max(0, final_revenue)
    
    # --- 7. Update Game State ---
    game.state["passengers"] = boarding_passengers
    
    # Add to treasury
    game.state["treasury"] += final_revenue
    
    # Mark as unavailable until next travel
    game.state["passenger_transport_available"] = False
    
    # Log Transaction
    if "transactions" not in game.state:
        game.state["transactions"] = []
    
    game.state["transactions"].append({
        "date": GameCalendar.date_to_string(game.state.get("year", 1), game.state.get("month", 1), game.state.get("day", 1)),
        "amount": final_revenue,
        "category": "comercio",
        "description": f"Transporte de {boarding_passengers} pasajeros"
    })
    
    game.record_dice_roll(2, dice_values, is_manual, "passenger_transport")
    game.save()
    db.commit()
    
    # Log Event
    EventLogger._log_to_game(
        game, 
        f"✈️ Embarque de Pasajeros: {boarding_passengers} pax. Ingresos: {final_revenue} SC.",
        "success" if final_revenue > 0 else "info"
    )

    return {
        "status": "success",
        "dice": dice_values,
        "modifiers": mods_detail,
        "total_roll": final_result,
        "outcome": outcome_type,
        "passengers": {
            "calculated": raw_passengers,
            "boarded": boarding_passengers,
            "capacity": ship_capacity
        },
        "revenue": {
            "base": base_revenue,
            "multiplier": multiplier,
            "novice_penalty": novice_penalty,
            "veteran_bonus": veteran_bonus,
            "total": final_revenue
        },
        "personnel_changes": personnel_changes
    }


# ===== TRADING API =====

@router.get("/api/games/{game_id}/trade/market")
async def get_trade_market(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener productos disponibles para comprar y órdenes activas."""
    from app.trade_manager import TradeManager
    
    game = GameState(game_id)
    planet_code = game.state.get("current_planet_code")
    if not planet_code:
        raise HTTPException(status_code=400, detail="Ship not on a planet")
        
    manager = TradeManager(game_id, db)
    market_data = manager.get_market_data(planet_code)
    
    return market_data


@router.get("/api/games/{game_id}/trade/orders")
async def get_trade_orders(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener todas las órdenes de comercio (libro de operaciones)."""
    orders = db.query(TradeOrder).filter(TradeOrder.game_id == game_id).all()
    
    # Convertir objetos SQLAlchemy a diccionarios para serialización JSON
    orders_dict = []
    for order in orders:
        orders_dict.append({
            "id": order.id,
            "game_id": order.game_id,
            "area": order.area,
            "buy_planet_code": order.buy_planet_code,
            "buy_planet_name": order.buy_planet_name,
            "product_code": order.product_code,
            "quantity": order.quantity,
            "buy_price_per_unit": order.buy_price_per_unit,
            "total_buy_price": order.total_buy_price,
            "buy_date": order.buy_date,
            "traceability": order.traceability,
            "status": order.status,
            "sell_planet_code": order.sell_planet_code,
            "sell_planet_name": order.sell_planet_name,
            "sell_price_total": order.sell_price_total,
            "sell_date": order.sell_date,
            "profit": order.profit,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        })
    
    return {"orders": orders_dict}


@router.post("/api/games/{game_id}/trade/negotiate")
async def negotiate_trade(
    game_id: str,
    action: str = Form(...),
    manual_roll: Optional[int] = Form(None)
) -> Dict[str, Any]:
    """Simular la tirada de negociación.

    Devuelve modificadores y resultados pero NO ejecuta la transacción.
    Avanza el tiempo según los días consumidos por la negociación.
    """
    from app.trade_manager import TradeManager
    
    game = GameState(game_id)
    negotiator_skill = 0 
    reputation = game.state.get("reputation", 0)
    
    manager = TradeManager(game_id, None) 
    result = manager.negotiate_price(
        negotiator_skill=negotiator_skill, 
        reputation=reputation, 
        is_buy=(action == "buy"),
        manual_roll=manual_roll
    )
    
    # Avanzar tiempo (la negociación consume tiempo)
    days = result.get("days_consumed", 0)
    if days > 0:
        new_date_str = advance_game_time(game, days)
        # Añadir al resultado para información de la UI
        result["new_date"] = new_date_str
    
    return result


@router.post("/api/games/{game_id}/trade/buy-batch")
async def execute_trade_buy_batch(
    game_id: str,
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ejecutar una transacción de compra en lote (cesta de compra).
    
    Acepta un cuerpo JSON con `planet_code` e `items` (lista de productos).
    Avanza el tiempo según los días de carga necesarios.
    """
    from app.trade_manager import TradeManager
    
    data = await request.json()
    planet_code = data.get("planet_code")
    items = data.get("items", [])
    
    if not items or planet_code is None:
        raise HTTPException(status_code=400, detail="Missing items or planet_code")
    
    # Asegurar que planet_code es un entero
    try:
        planet_code = int(planet_code)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="planet_code debe ser un número entero")
    
    # Validar formato de items
    if not isinstance(items, list):
        raise HTTPException(status_code=400, detail="items debe ser una lista")
    
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail="Cada item debe ser un objeto")
        required_fields = ["product_code", "quantity", "unit_price"]
        for field in required_fields:
            if field not in item:
                raise HTTPException(status_code=400, detail=f"Falta el campo '{field}' en un item")
        
    manager = TradeManager(game_id, db)
    result = manager.execute_batch_buy(items, planet_code)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    # Avanzar tiempo para la carga
    loading_days = result.get("loading_days", 0)
    if loading_days > 0:
        game = GameState(game_id)
        new_date_str = advance_game_time(game, loading_days)
        result["new_date"] = new_date_str
        
    return result


@router.post("/api/games/{game_id}/trade/buy")
async def execute_trade_buy(
    game_id: str,
    planet_code: int = Form(...),
    product_code: str = Form(...),
    quantity: int = Form(...),
    unit_price: int = Form(...),
    traceability: bool = Form(True),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ejecutar una transacción de compra."""
    from app.trade_manager import TradeManager
    
    manager = TradeManager(game_id, db)
    result = manager.execute_buy(
        planet_code=planet_code,
        product_code=product_code,
        quantity=quantity,
        unit_price=unit_price,
        traceability=traceability
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result


@router.post("/api/games/{game_id}/trade/sell")
async def execute_trade_sell(
    game_id: str,
    order_id: int = Form(...),
    planet_code: int = Form(...),
    sell_price_total: int = Form(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ejecutar una transacción de venta."""
    from app.trade_manager import TradeManager
    
    manager = TradeManager(game_id, db)
    result = manager.execute_sell(
        order_id=order_id,
        planet_code=planet_code,
        sell_price_total=sell_price_total
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result
