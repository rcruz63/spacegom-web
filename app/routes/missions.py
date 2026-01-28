"""
Routes para gestión de misiones.

CRUD de misiones vía GameState (DynamoDB).
"""
from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter, Form, HTTPException

from app.game_state import GameState
from app.time_manager import GameCalendar, EventQueue

router = APIRouter(tags=["missions"])


@router.get("/api/games/{game_id}/missions")
async def get_missions(game_id: str) -> Dict[str, Any]:
    """Obtiene todas las misiones de una partida, separadas por estado."""
    game = GameState(game_id)
    missions = game.get_missions()
    active = []
    completed = []
    failed = []
    for m in missions:
        mission_data = {
            "id": m["id"],
            "mission_type": m["mission_type"],
            "origin_world": m.get("origin_world"),
            "execution_place": m.get("execution_place"),
            "max_date": m.get("max_date"),
            "result": m.get("result", ""),
            "created_date": m.get("created_date"),
            "completed_date": m.get("completed_date"),
            "notes": m.get("notes", ""),
        }
        if m.get("mission_type") == "campaign":
            mission_data["objective_number"] = m.get("objective_number")
        else:
            mission_data["mission_code"] = m.get("mission_code")
            mission_data["book_page"] = m.get("book_page")
        res = m.get("result", "")
        if res == "exito":
            completed.append(mission_data)
        elif res == "fracaso":
            failed.append(mission_data)
        else:
            active.append(mission_data)
    return {"active": active, "completed": completed, "failed": failed, "total": len(missions)}


@router.post("/api/games/{game_id}/missions")
async def create_mission(
    game_id: str,
    mission_type: str = Form(...),
    origin_world: str = Form(""),
    execution_place: str = Form(...),
    max_date: str = Form(""),
    notes: str = Form(""),
    objective_number: Optional[int] = Form(None),
    mission_code: Optional[str] = Form(None),
    book_page: Optional[int] = Form(None),
) -> Dict[str, Any]:
    """Crea una nueva misión (objetivo de campaña o misión especial)."""
    from app.event_logger import EventLogger

    if mission_type not in ["campaign", "special"]:
        raise HTTPException(status_code=400, detail="Mission type must be 'campaign' or 'special'")
    if mission_type == "campaign" and objective_number is None:
        raise HTTPException(status_code=400, detail="objective_number required for campaign missions")
    if mission_type == "special" and (not mission_code or book_page is None):
        raise HTTPException(status_code=400, detail="mission_code and book_page required for special missions")

    game = GameState(game_id)
    data: Dict[str, Any] = {
        "mission_type": mission_type,
        "origin_world": origin_world or "",
        "execution_place": execution_place,
        "max_date": max_date or "",
        "created_date": date.today().isoformat(),
        "notes": notes or "",
        "result": "",
    }
    if mission_type == "campaign":
        data["objective_number"] = objective_number
        data["mission_code"] = None
        data["book_page"] = None
    else:
        data["objective_number"] = None
        data["mission_code"] = mission_code
        data["book_page"] = book_page

    mission_id = game.add_mission(data)
    if mission_type == "campaign":
        mission_desc = f"Objetivo #{objective_number} de campaña"
    else:
        mission_desc = f"Misión especial {mission_code} (pág. {book_page})"

    EventLogger._log_to_game(game, f"🎯 Nueva misión: {mission_desc} en {execution_place}", event_type="info")

    if max_date:
        game.state["event_queue"] = EventQueue.add_event(
            game.state.get("event_queue", []),
            "mission_deadline",
            max_date,
            {"mission_id": mission_id, "mission_type": mission_type, "objective": mission_desc},
        )
        game.save()
        EventLogger._log_to_game(game, f"📅 Fecha límite de misión programada: {max_date}", event_type="info")

    return {"status": "success", "mission_id": mission_id, "mission_type": mission_type}


@router.put("/api/games/{game_id}/missions/{mission_id}")
async def update_mission_result(
    game_id: str,
    mission_id: int,
    result: str = Form(...),
    completed_date: str = Form(""),
    notes: Optional[str] = Form(None),
) -> Dict[str, Any]:
    """Actualizar el resultado de una misión (marcar como éxito o fracaso)."""
    game = GameState(game_id)
    mission = game.get_mission_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if result not in ["exito", "fracaso", ""]:
        raise HTTPException(status_code=400, detail="Result must be 'exito', 'fracaso', or empty")
    updates: Dict[str, Any] = {"result": result}
    if completed_date:
        updates["completed_date"] = completed_date
    if notes is not None:
        updates["notes"] = notes
    game.update_mission(mission_id, updates)
    return {"status": "success", "mission_id": mission_id, "result": result}


@router.post("/api/games/{game_id}/missions/{mission_id}/resolve")
async def resolve_mission_deadline(
    game_id: str,
    mission_id: int,
    success: bool = Form(...),
) -> Dict[str, Any]:
    """Resuelve la fecha límite de una misión (éxito/fracaso). Éxito: +1 reputación; fracaso: -1."""
    from app.event_logger import EventLogger

    game = GameState(game_id)
    mission = game.get_mission_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    current_date = GameCalendar.date_to_string(
        game.state.get("year", 1),
        game.state.get("month", 1),
        game.state.get("day", 1),
    )
    result_val = "exito" if success else "fracaso"
    game.update_mission(mission_id, {"result": result_val, "completed_date": current_date})

    if success:
        game.state["reputation"] = game.state.get("reputation", 0) + 1
    else:
        game.state["reputation"] = max(0, game.state.get("reputation", 0) - 1)

    game.state["event_queue"] = [
        e for e in game.state.get("event_queue", [])
        if not (e.get("type") == "mission_deadline" and e.get("data", {}).get("mission_id") == mission_id)
    ]
    game.save()

    if mission.get("mission_type") == "campaign":
        mission_desc = f"Objetivo #{mission.get('objective_number')}"
    else:
        mission_desc = f"Misión {mission.get('mission_code')}"
    result_text = "completada con éxito ✅" if success else "fallida ❌"
    EventLogger._log_to_game(
        game,
        f"🎯 Misión {result_text}: {mission_desc}. Reputación: {game.state.get('reputation', 0)}",
        event_type="success" if success else "warning",
    )
    return {
        "status": "resolved",
        "success": success,
        "new_reputation": game.state.get("reputation", 0),
        "mission_result": result_val,
    }


@router.delete("/api/games/{game_id}/missions/{mission_id}")
async def delete_mission(game_id: str, mission_id: int) -> Dict[str, Any]:
    """Eliminar una misión de la base de datos."""
    game = GameState(game_id)
    if not game.get_mission_by_id(mission_id):
        raise HTTPException(status_code=404, detail="Mission not found")
    game.delete_mission(mission_id)
    return {"status": "success", "deleted_id": mission_id}
