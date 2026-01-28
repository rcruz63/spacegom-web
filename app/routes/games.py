"""
Routes para gestión de juegos.

Este módulo contiene los endpoints relacionados con:
- CRUD de juegos (crear, listar, obtener estado)
- Configuración inicial (setup)
- Avance de tiempo
- Exploración de cuadrantes
"""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter, Form, HTTPException

from app.database import INITIAL_PERSONNEL
from app.game_state import GameState
from app.dice import DiceRoller
from app.time_manager import GameCalendar, EventQueue

router = APIRouter(tags=["games"])


# ===== GAME MANAGEMENT API =====

@router.get("/api/games")
async def list_games() -> Dict[str, Any]:
    """
    Lista todas las partidas guardadas disponibles.
    
    Retorna información básica de cada partida incluyendo ID, fechas de
    creación y actualización, mes actual y créditos.
    
    Returns:
        Diccionario con clave "games" conteniendo lista de partidas ordenadas
        por fecha de actualización (más recientes primero)
    """
    games = GameState.list_games()
    return {"games": games}


@router.post("/api/games/new")
async def create_game(game_name: Optional[str] = Form(None)) -> Dict[str, Any]:
    """
    Crea una nueva partida con ID único.
    
    Si no se proporciona nombre, genera uno automáticamente basado en timestamp.
    Inicializa el estado del juego con valores por defecto.
    
    Args:
        game_name: Nombre opcional para la partida (se limpia para crear ID válido)
    
    Returns:
        Diccionario con "game_id" y "state" (estado inicial completo)
    """
    game = GameState.create_new_game(game_name)
    game.save()
    return {"game_id": game.game_id, "state": game.state}


@router.get("/api/games/{game_id}")
async def get_game_state(game_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado completo del juego incluyendo estadísticas de la nave.
    
    Carga el estado persistido desde el archivo JSON y obtiene las estadísticas
    de la nave desde ship_data.py basándose en el modelo guardado.
    
    Args:
        game_id: Identificador único de la partida
    
    Returns:
        Diccionario con:
        - "state": Estado completo del juego (diccionario JSON)
        - "ship_stats": Estadísticas de la nave (capacidad, daños, coste, etc.)
    """
    from app.ship_data import get_ship_stats
    game = GameState(game_id)
    ship_stats = get_ship_stats(game.state.get("ship_model", "Basic Starfall"))
    return {
        "state": game.state,
        "ship_stats": ship_stats
    }


@router.post("/api/games/{game_id}/update")
async def update_game_state(
    game_id: str,
    fuel: Optional[int] = Form(None),
    storage: Optional[int] = Form(None),
    month: Optional[int] = Form(None),
    reputation: Optional[int] = Form(None),
    damage_light: Optional[bool] = Form(None),
    damage_moderate: Optional[bool] = Form(None),
    damage_severe: Optional[bool] = Form(None)
) -> Dict[str, Any]:
    """Actualizar campos del estado del juego.

    Realiza validaciones básicas y límites (por ejemplo, combustible entre
    0 y `fuel_max`) y actualiza indicadores booleanos de daños.
    Devuelve el estado actualizado.
    """
    game = GameState(game_id)
    
    if fuel is not None:
        game.state["fuel"] = max(0, min(game.state["fuel_max"], fuel))
    if storage is not None:
        game.state["storage"] = max(0, min(game.state["storage_max"], storage))
    if month is not None:
        game.state["month"] = max(1, min(12, month))
    if reputation is not None:
        game.state["reputation"] = max(-5, min(5, reputation))
    
    if damage_light is not None:
        game.state["damages"]["light"] = damage_light
    if damage_moderate is not None:
        game.state["damages"]["moderate"] = damage_moderate
    if damage_severe is not None:
        game.state["damages"]["severe"] = damage_severe
    
    game.save()
    return {"state": game.state}


@router.get("/api/games/{game_id}/logs")
async def get_logs(
    game_id: str,
    limit: Optional[int] = None,
    event_type: Optional[str] = None
) -> Dict[str, Any]:
    """Obtener registros de eventos del juego.

    Soporta filtros `limit` y `event_type`. Devuelve la lista `logs` y el
    recuento `count`.
    """
    from app.event_logger import EventLogger
    
    logger = EventLogger(game_id)
    logs = logger.get_logs(limit=limit, event_type=event_type)
    
    return {
        "logs": logs,
        "count": len(logs)
    }


@router.post("/api/games/{game_id}/update-location")
async def update_ship_location(
    game_id: str,
    location: str = Form(...)
) -> Dict[str, Any]:
    """Actualizar la ubicación de la nave en el planeta (por ejemplo, "Mundo", "Espaciopuerto")."""
    game = GameState(game_id)
    game.state["ship_location_on_planet"] = location
    game.save()
    return {"status": "success", "location": location}


@router.post("/api/games/{game_id}/company-setup")
async def company_setup(
    game_id: str,
    company_name: str = Form(...),
    ship_name: str = Form(...),
    ship_model: str = Form("Basic Starfall")
) -> Dict[str, Any]:
    """Guardar los datos de la compañía y la nave del jugador.

    Inicializa estadísticas de la nave en función del `ship_model`.
    """
    from app.ship_data import get_ship_stats
    
    game = GameState(game_id)
    game.state["company_name"] = company_name
    game.state["ship_name"] = ship_name
    game.state["ship_model"] = ship_model
    
    # Initialize ship stats from model
    stats = get_ship_stats(ship_model)
    game.state["fuel_max"] = stats["jump"] * 30
    game.state["storage_max"] = stats["storage"]
    
    game.save()
    return {"status": "success", "state": game.state}


@router.post("/api/games/{game_id}/setup")
async def initial_company_setup(
    game_id: str,
    area_manual: Optional[str] = Form(None),
    density_manual: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Configuración inicial de la compañía.

    Paso 1: tirar 2d6 para área espacial (2-12).
    Paso 2: tirar 2d6 para densidad de mundos y determinar nivel:
        - 2-4: Baja
        - 5-9: Media
        - 10-12: Alta

    Parámetros opcionales `area_manual` y `density_manual` permiten
    proporcionar resultados manuales separados por comas.
    """
    game = GameState(game_id)
    
    # Step 1: Determine area (2d6)
    area_is_manual = False
    area_results = []
    
    if area_manual and area_manual.strip():
        try:
            area_results = [int(x.strip()) for x in area_manual.split(",")]
            if len(area_results) != 2:
                raise ValueError("Need exactly 2 dice for area")
            if any(r < 1 or r > 6 for r in area_results):
                raise ValueError("Dice results must be between 1 and 6")
            area_is_manual = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid area_manual: {e}")
    else:
        area_results = DiceRoller.roll_dice(num_dice=2)
    
    area = sum(area_results)
    game.record_dice_roll(2, area_results, area_is_manual, "initial_area")
    
    # Step 2: Determine world density (2d6)
    density_is_manual = False
    density_results = []
    
    if density_manual and density_manual.strip():
        try:
            density_results = [int(x.strip()) for x in density_manual.split(",")]
            if len(density_results) != 2:
                raise ValueError("Need exactly 2 dice for density")
            if any(r < 1 or r > 6 for r in density_results):
                raise ValueError("Dice results must be between 1 and 6")
            density_is_manual = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid density_manual: {e}")
    else:
        density_results = DiceRoller.roll_dice(num_dice=2)
    
    density_total = sum(density_results)
    world_density = DiceRoller.world_density_from_roll(density_total)
    game.record_dice_roll(2, density_results, density_is_manual, "world_density")
    
    # Update game state
    game.state["area"] = area
    game.state["current_area"] = area
    game.state["world_density"] = world_density
    game.state["setup_complete"] = True
    
    game.add_event(
        "initial_setup",
        f"Empresa establecida en Área {area} con densidad de mundos {world_density}",
        {
            "area": area,
            "world_density": world_density,
            "area_roll": area_results,
            "density_roll": density_results
        }
    )
    
    game.save()
    
    return {
        "area": {
            "value": area,
            "dice": area_results,
            "is_manual": area_is_manual
        },
        "world_density": {
            "level": world_density,
            "total": density_total,
            "dice": density_results,
            "is_manual": density_is_manual
        },
        "setup_complete": True,
        "state": game.state
    }


@router.post("/api/games/{game_id}/setup-position")
async def initial_position_setup(
    game_id: str,
    row_manual: Optional[int] = Form(None),
    col_manual: Optional[int] = Form(None)
) -> Dict[str, Any]:
    """Configuración inicial de la posición de la nave.

    Se tiran 1d6 para fila y 1d6 para columna (valores 1-6).
    """
    game = GameState(game_id)
    
    # Row setup
    row_is_manual = False
    if row_manual is not None:
        if 1 <= row_manual <= 6:
            row_results = [row_manual]
            row_is_manual = True
        else:
            raise HTTPException(status_code=400, detail="Row dice must be between 1 and 6")
    else:
        row_results = DiceRoller.roll_dice(num_dice=1)
    
    row_val = row_results[0]
    game.record_dice_roll(1, row_results, row_is_manual, "initial_row")
    
    # Col setup
    col_is_manual = False
    if col_manual is not None:
        if 1 <= col_manual <= 6:
            col_results = [col_manual]
            col_is_manual = True
        else:
            raise HTTPException(status_code=400, detail="Col dice must be between 1 and 6")
    else:
        col_results = DiceRoller.roll_dice(num_dice=1)
        
    col_val = col_results[0]
    game.record_dice_roll(1, col_results, col_is_manual, "initial_col")
    
    # Update game state (storing 1-6 in ship_row/ship_col for display)
    game.state["ship_row"] = row_val
    game.state["ship_col"] = col_val
    game.state["ship_pos_complete"] = True
    
    # First exploration of current quadrant (internal storage uses 0-based)
    game.explore_quadrant(row_val - 1, col_val - 1)
    
    game.add_event(
        "initial_position",
        f"Posición inicial establecida en Cuadrante {chr(64+col_val)}{row_val}",
        {"row": row_val, "col": col_val}
    )
    
    game.save()
    
    return {
        "row": row_val,
        "col": col_val,
        "col_letter": chr(64+col_val),
        "ship_pos_complete": True,
        "state": game.state
    }


# ===== EXPLORATION API =====

@router.post("/api/games/{game_id}/explore")
async def explore_quadrant(
    game_id: str,
    row: int = Form(...),
    col: int = Form(...)
) -> Dict[str, Any]:
    """Marcar un cuadrante como explorado.

    Actualiza el estado del juego para reflejar la exploración y devuelve
    la lista actualizada de cuadrantes explorados.
    """
    game = GameState(game_id)
    game.explore_quadrant(row, col)
    
    return {
        "explored": True,
        "quadrant": f"{row},{col}",
        "explored_quadrants": game.state["explored_quadrants"]
    }


@router.post("/api/games/{game_id}/navigate-area")
async def navigate_area(
    game_id: str,
    direction: str = Form(...)
) -> Dict[str, Any]:
    """Navegar a un área adyacente (anterior/siguiente).

    Args:
        game_id: Identificador de la partida.
        direction: "prev" o "next" indicando dirección.

    Returns:
        JSON con el nuevo número de área y el estado de la operación.
    """
    game = GameState(game_id)
    current_area = game.state.get("area", 2)
    
    if direction == "prev" and current_area > 2:
        game.state["area"] = current_area - 1
        game.save()
        return {"success": True, "new_area": current_area - 1}
    elif direction == "next" and current_area < 12:
        game.state["area"] = current_area + 1
        game.save()
        return {"success": True, "new_area": current_area + 1}
    else:
        return {"success": False, "new_area": current_area, "message": "Area limit reached"}


@router.get("/api/games/{game_id}/area/{area_number}/planets")
async def get_area_planets(
    game_id: str,
    area_number: int,
) -> Dict[str, Any]:
    """
    Get all discovered planets in a specific area.
    """
    from app.routes.planets import format_planet_data
    from app.planets_repo import get_planet_by_code

    game = GameState(game_id)

    area_planets = []
    for code, info in game.state.get("discovered_planets", {}).items():
        if info["area"] == area_number:
            planet = get_planet_by_code(int(code))
            if planet:
                planet_data = format_planet_data(planet)
                planet_data["quadrant"] = info["quadrant"]
                area_planets.append(planet_data)
    
    # Get current ship position info
    current_planet_code = game.state.get("current_planet_code")
    ship_quadrant = f"{game.state.get('ship_row')},{game.state.get('ship_col')}"
    
    return {
        "planets": area_planets,
        "area": area_number,
        "count": len(area_planets),
        "current_planet_code": current_planet_code,
        "ship_quadrant": ship_quadrant
    }


# ===== TIME ADVANCE API =====

@router.post("/api/games/{game_id}/time/advance")
async def advance_time(
    game_id: str,
    manual_dice: Optional[str] = Form(None),
):
    """Avanza el tiempo al próximo evento y lo procesa con el sistema de handlers."""
    import traceback

    from app.event_handlers import get_event_handler

    game = GameState(game_id)
    event_queue = game.state.get("event_queue", [])
    if not event_queue:
        return {"status": "no_events", "message": "No hay eventos pendientes"}

    next_event = EventQueue.get_next_event(event_queue)
    if not next_event:
        return {"status": "no_events"}

    old_date = GameCalendar.date_to_string(
        game.state.get("year", 1),
        game.state.get("month", 1),
        game.state.get("day", 1),
    )
    new_year, new_month, new_day = GameCalendar.parse_date(next_event["date"])
    game.state["year"] = new_year
    game.state["month"] = new_month
    game.state["day"] = new_day
    game.save()

    handler = get_event_handler(next_event["type"])
    if not handler:
        return {"status": "error", "message": f"No handler for event type: {next_event['type']}"}

    try:
        result = handler(next_event, game, manual_dice)
        if result.remove_from_queue:
            game.state["event_queue"] = EventQueue.remove_event(
                game.state.get("event_queue", []),
                next_event,
            )
            game.save()
        return {
            "status": "success",
            "old_date": old_date,
            "new_date": next_event["date"],
            "event_result": result.to_dict(),
        }
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# ===== SETUP COMPLETION =====

@router.post("/api/games/{game_id}/complete-setup")
async def complete_setup(game_id: str, difficulty: str = Form(...)):
    """Completa el setup con dificultad y crea el personal inicial."""
    from app.event_logger import EventLogger

    game = GameState(game_id)
    difficulty_funds = {"easy": 600, "normal": 500, "hard": 400}
    if difficulty not in difficulty_funds:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")

    game.state["difficulty"] = difficulty
    game.state["treasury"] = difficulty_funds[difficulty]
    game.state["reputation"] = 0
    game.state["setup_complete"] = True
    game.save()

    company_name = game.state.get("company_name", "Compañía Desconocida")
    ship_name = game.state.get("ship_name", "Nave Sin Nombre")
    current_planet = game.state.get("current_planet_code", "???")
    EventLogger._log_to_game(
        game,
        f"📜 La empresa {company_name} inicia sus operaciones con la nave {ship_name} desde el planeta {current_planet}. "
        f"Dificultad: {difficulty.upper()}. Fondos iniciales: {difficulty_funds[difficulty]} SC",
        event_type="success",
    )

    hire_date = date.today().isoformat()
    for emp_data in INITIAL_PERSONNEL:
        game.add_personnel({
            "position": emp_data["position"],
            "name": emp_data["name"],
            "monthly_salary": emp_data["salary"],
            "experience": emp_data["exp"],
            "morale": emp_data["morale"],
            "hire_date": hire_date,
            "is_active": True,
        })

    for emp_data in INITIAL_PERSONNEL:
        EventLogger._log_to_game(
            game,
            f"👥 {emp_data['name']} se une como {emp_data['position']} por {emp_data['salary']} SC/mes",
            event_type="info",
        )

    total_salaries = sum(emp["salary"] for emp in INITIAL_PERSONNEL)
    current_date = GameCalendar.date_to_string(
        game.state.get("year", 1),
        game.state.get("month", 1),
        game.state.get("day", 1),
    )
    next_salary_date = GameCalendar.next_day_35(current_date)
    game.state.setdefault("event_queue", [])
    game.state["event_queue"] = EventQueue.add_event(
        game.state.get("event_queue", []),
        "salary_payment",
        next_salary_date,
        {"monthly_payment": True},
    )
    game.save()
    EventLogger._log_to_game(
        game,
        f"📅 Próximo pago de salarios programado para el día 35 ({next_salary_date})",
        event_type="info",
    )
    return {
        "status": "success",
        "difficulty": difficulty,
        "starting_funds": difficulty_funds[difficulty],
        "personnel_count": len(INITIAL_PERSONNEL),
        "monthly_salaries": total_salaries,
    }
