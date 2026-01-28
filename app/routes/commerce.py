"""
Routes para tesorería, comercio y transporte de pasajeros.

Usa GameState y TradeManager (DynamoDB); sin SQL.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Form, HTTPException, Request

from app.planets_repo import get_planet_by_code
from app.game_state import GameState
from app.dice import DiceRoller
from app.time_manager import GameCalendar

router = APIRouter(tags=["commerce"])


# ===== HELPER FUNCTIONS =====

def advance_game_time(game: GameState, days: int) -> str:
    """
    Avanza el tiempo del juego N días, manejando cambios de mes y año.
    
    Usa GameCalendar.add_days() para calcular la nueva fecha respetando el
    calendario personalizado del juego (35 días/mes, 12 meses/año).
    
    Args:
        game: Instancia de GameState del juego
        days: Número de días a avanzar (debe ser positivo)
        
    Returns:
        Nueva fecha en formato string "dd-mm-yy"
        
    Note:
        Actualmente avanza directamente sin procesar eventos día a día.
        Para implementación completa, debería procesar eventos de la cola
        durante el avance.
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
async def get_treasury(game_id: str) -> Dict[str, Any]:
    """Obtiene información completa de la tesorería de una partida."""
    game = GameState(game_id)
    personnel = game.get_personnel(active_only=True)
    total_salaries = sum(p["monthly_salary"] for p in personnel)
    return {
        "current_balance": game.state.get("treasury", 0),
        "difficulty": game.state.get("difficulty"),
        "reputation": game.state.get("reputation", 0),
        "monthly_expenses": {"salaries": total_salaries, "loans": 0, "total": total_salaries},
        "recent_transactions": game.state.get("transactions", [])[-10:],
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
    game_date = GameCalendar.date_to_string(
        game.state.get("year", 1),
        game.state.get("month", 1),
        game.state.get("day", 1),
    )
    transaction = {"date": game_date, "amount": amount, "description": description, "category": category}
    game.append_transaction(transaction)
    game.state["treasury"] = game.state.get("treasury", 0) + amount
    game.save()
    return {"status": "success", "new_balance": game.state["treasury"], "transaction": transaction}


# ===== PASSENGER TRANSPORT API =====

@router.get("/api/games/{game_id}/passenger-transport/info")
async def get_passenger_transport_info(game_id: str) -> Dict[str, Any]:
    """
    Obtiene información para la acción de transporte de pasajeros.
    
    Calcula capacidad disponible, modificadores (responsable, auxiliares),
    promedio de pasajeros del planeta y estado de disponibilidad de la acción.
    
    Args:
        game_id: Identificador único de la partida
        db: Sesión de base de datos SQLAlchemy
    
    Returns:
        Diccionario con:
        - "current_passengers": Pasajeros actuales a bordo
        - "ship_capacity": Capacidad máxima de la nave
        - "planet_avg_passengers": Promedio de pasajeros del planeta
        - "modifiers": {has_manager, manager_bonus, manager_name, attendants_count}
        - "available": True si la acción está disponible (se resetea al viajar)
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
        planet = get_planet_by_code(planet_code)
        if planet:
            avg_passengers = planet.max_passengers
            
    personnel = game.get_personnel(active_only=True)
    manager = next((p for p in personnel if p.get("position") == "Responsable de soporte a pasajeros"), None)
    manager_bonus = 0
    if manager:
        exp_mod = {"N": -1, "E": 0, "V": 1}.get(manager.get("experience", "N"), 0)
        morale_mod = {"B": -1, "M": 0, "A": 1}.get(manager.get("morale", "M"), 0)
        rep_mod = math.floor(game.state.get("reputation", 0) / 2)
        manager_bonus = exp_mod + morale_mod + rep_mod
    attendants_count = sum(1 for p in personnel if p.get("position") == "Auxiliar de vuelo")

    return {
        "ship_capacity": ship_capacity,
        "current_passengers": current_passengers,
        "planet_avg_passengers": avg_passengers,
        "modifiers": {
            "has_manager": manager is not None,
            "manager_name": manager["name"] if manager else None,
            "manager_bonus": manager_bonus,
            "attendants_count": attendants_count,
        },
        "location": game.state.get("ship_location_on_planet", "Mundo"),
        "available": game.state.get("passenger_transport_available", True),
    }


@router.post("/api/games/{game_id}/passenger-transport/execute")
async def execute_passenger_transport(
    game_id: str,
    manual_dice: Optional[str] = Form(None),
) -> Dict[str, Any]:
    """
    Ejecuta la acción de transporte de pasajeros.
    
    Proceso completo:
    1. Tira 2d6 para determinar afluencia (con modificadores)
    2. Calcula número de pasajeros según afluencia (Alta x2, Baja /2, Media x1)
    3. Calcula ingresos (base * multiplicador de auxiliares + bonus XP)
    4. Actualiza moral/experiencia del personal según resultado
    5. Registra evento en el log
    
    Args:
        game_id: Identificador único de la partida
        manual_dice: Opcional string con resultados manuales separados por comas (ej: "4,6")
        db: Sesión de base de datos SQLAlchemy
    
    Returns:
        Diccionario con:
        - "status": "success"
        - "dice": Valores de los dados
        - "total_roll": Total con modificadores
        - "outcome": "high", "medium", o "low"
        - "passengers": {boarded, capacity}
        - "revenue": {base, multiplier, veteran_bonus, novice_penalty, total}
        - "modifiers": Modificadores aplicados
        - "personnel_changes": Cambios en personal (opcional)
    
    Raises:
        HTTPException 400: Si la acción no está disponible o hay error
    """
    from app.personnel_manager import update_employee_roll_stats
    from app.ship_data import get_ship_stats
    from app.event_logger import EventLogger
    
    game = GameState(game_id)
    
    # --- 1. Basic Checks ---
    if not game.state.get("passenger_transport_available", True):
        raise HTTPException(400, "Transporte de pasajeros ya realizado en esta visita. Debes viajar a otro cuadrante y volver.")

    planet_code = game.state.get("current_planet_code")
    planet = get_planet_by_code(planet_code)
    if not planet:
        raise HTTPException(400, "Not on a known planet")
        
    avg_passengers = planet.max_passengers
    ship_stats = get_ship_stats(game.state.get("ship_model", "Basic Starfall"))
    ship_capacity = ship_stats.get("passengers", 10)
    
    personnel = game.get_personnel(active_only=True)
    manager = next((p for p in personnel if p.get("position") == "Responsable de soporte a pasajeros"), None)
    
    total_mod = 0
    mods_detail = {}
    
    if manager:
        exp_mod = {"N": -1, "E": 0, "V": 1}.get(manager.get("experience", "N"), 0)
        morale_mod = {"B": -1, "M": 0, "A": 1}.get(manager.get("morale", "M"), 0)
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
    
    personnel_changes = None
    if manager:
        personnel_changes = update_employee_roll_stats(manager, dice_values, final_result)
        game.update_personnel(manager["id"], {"morale": manager["morale"], "experience": manager["experience"]})
        for msg in personnel_changes["messages"]:
            EventLogger._log_to_game(game, f"👔 {manager.get('name')}: {msg}", "info")

    flight_attendants = [p for p in personnel if p.get("position") == "Auxiliar de vuelo"]
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
async def get_trade_market(game_id: str) -> Dict[str, Any]:
    """Obtiene datos del mercado comercial en el planeta actual."""
    from app.trade_manager import TradeManager

    game = GameState(game_id)
    planet_code = game.state.get("current_planet_code")
    if not planet_code:
        raise HTTPException(status_code=400, detail="Ship not on a planet")
    manager = TradeManager(game_id)
    return manager.get_market_data(planet_code)


@router.get("/api/games/{game_id}/trade/orders")
async def get_trade_orders(game_id: str) -> Dict[str, Any]:
    """Obtiene todas las órdenes de comercio de una partida."""
    game = GameState(game_id)
    orders = game.get_trade_orders()
    orders_dict = [
        {
            "id": o["id"],
            "game_id": o.get("game_id", game_id),
            "area": o.get("area"),
            "buy_planet_code": o.get("buy_planet_code"),
            "buy_planet_name": o.get("buy_planet_name"),
            "product_code": o.get("product_code"),
            "quantity": o.get("quantity"),
            "buy_price_per_unit": o.get("buy_price_per_unit"),
            "total_buy_price": o.get("total_buy_price"),
            "buy_date": o.get("buy_date"),
            "traceability": o.get("traceability"),
            "status": o.get("status"),
            "sell_planet_code": o.get("sell_planet_code"),
            "sell_planet_name": o.get("sell_planet_name"),
            "sell_price_total": o.get("sell_price_total"),
            "sell_date": o.get("sell_date"),
            "profit": o.get("profit"),
            "created_at": o.get("created_at"),
            "updated_at": o.get("updated_at"),
        }
        for o in orders
    ]
    return {"orders": orders_dict}


@router.post("/api/games/{game_id}/trade/negotiate")
async def negotiate_trade(
    game_id: str,
    action: str = Form(...),
    manual_roll: Optional[int] = Form(None)
) -> Dict[str, Any]:
    """
    Simula la tirada de negociación de comercio.
    
    Calcula el multiplicador de precio basado en tirada de 2d6 + modificadores,
    pero NO ejecuta la transacción. El cliente debe llamar a /buy o /sell después
    con el precio negociado.
    
    Avanza el tiempo del juego según los días consumidos por la negociación
    (1 día para compra, 1d6 días para venta).
    
    Args:
        game_id: Identificador único de la partida
        action: "buy" o "sell"
        manual_roll: Opcional resultado manual de tirada (dados físicos)
    
    Returns:
        Diccionario con resultado de TradeManager.negotiate_price():
        - "roll", "dice", "modifiers", "total"
        - "multiplier": Multiplicador de precio (0.8, 1.0, 1.2)
        - "moral_effect": Efecto en moral ("Loss", "None", "Gain")
        - "days_consumed": Días consumidos por la negociación
    """
    from app.trade_manager import TradeManager
    
    game = GameState(game_id)
    negotiator_skill = 0 
    reputation = game.state.get("reputation", 0)
    
    manager = TradeManager(game_id)
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
async def execute_trade_buy_batch(game_id: str, request: Request) -> Dict[str, Any]:
    """
    Ejecuta una transacción de compra en lote (cesta de compra).
    
    Valida que hay fondos y capacidad suficientes para todo el lote antes
    de ejecutar ninguna compra. Si alguna validación falla, no se ejecuta
    ninguna compra (transacción atómica).
    
    Body JSON esperado:
    {
        "planet_code": int,
        "items": [
            {"product_code": str, "quantity": int, "unit_price": int},
            ...
        ]
    }
    
    Args:
        game_id: Identificador único de la partida
        request: Request de FastAPI con JSON body
        db: Sesión de base de datos SQLAlchemy
    
    Returns:
        Diccionario con resultado de TradeManager.execute_batch_buy():
        - "success": True si todas las compras fueron exitosas
        - "total_cost": Coste total del lote
        - "loading_days": Días necesarios para cargar
        - "orders": IDs de órdenes creadas
        - "error": Mensaje de error si success=False
    
    Raises:
        HTTPException 400: Si hay error en la validación o ejecución
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
        
    manager = TradeManager(game_id)
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
) -> Dict[str, Any]:
    """
    Ejecuta una transacción de compra individual.
    
    Valida tesorería y capacidad, descuenta costo, crea TradeOrder y actualiza
    almacenamiento y cargo. Registra transacción y evento en el log.
    
    Args:
        game_id: Identificador único de la partida
        planet_code: Código del planeta donde se compra (111-666)
        product_code: Código del producto (ej: "INDU", "BASI")
        quantity: Cantidad en UCN a comprar
        unit_price: Precio unitario negociado
        traceability: Si el producto tiene trazabilidad (default: True)
        db: Sesión de base de datos SQLAlchemy
    
    Returns:
        Diccionario con resultado de TradeManager.execute_buy():
        - "success": True si la compra fue exitosa
        - "order_id": ID de la orden creada
        - "balance": Saldo restante en tesorería
        - "error": Mensaje de error si success=False
    
    Raises:
        HTTPException 400: Si hay error en validación o ejecución
    """
    from app.trade_manager import TradeManager
    
    manager = TradeManager(game_id)
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
) -> Dict[str, Any]:
    """
    Ejecuta una transacción de venta de una orden existente.
    
    Actualiza la TradeOrder con datos de venta, calcula ganancia, agrega créditos
    a tesorería y actualiza almacenamiento. Registra transacción y evento.
    
    Args:
        game_id: Identificador único de la partida
        order_id: ID de la TradeOrder a vender
        planet_code: Código del planeta donde se vende (111-666)
        sell_price_total: Precio total de venta negociado
        db: Sesión de base de datos SQLAlchemy
    
    Returns:
        Diccionario con resultado de TradeManager.execute_sell():
        - "success": True si la venta fue exitosa
        - "profit": Ganancia obtenida (precio_venta - precio_compra)
        - "balance": Saldo actualizado en tesorería
        - "error": Mensaje de error si success=False
    
    Raises:
        HTTPException 400: Si la orden no existe o ya fue vendida
    """
    from app.trade_manager import TradeManager
    
    manager = TradeManager(game_id)
    result = manager.execute_sell(
        order_id=order_id,
        planet_code=planet_code,
        sell_price_total=sell_price_total
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result
