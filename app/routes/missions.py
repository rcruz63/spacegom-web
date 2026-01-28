"""
Routes para gestión de misiones.

Este módulo contiene los endpoints relacionados con:
- CRUD de misiones (campaña y especiales)
- Resolución de fechas límite de misiones
"""
from fastapi import APIRouter, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date

from app.database import get_db, Mission
from app.game_state import GameState
from app.time_manager import GameCalendar, EventQueue

router = APIRouter(tags=["missions"])


@router.get("/api/games/{game_id}/missions")
async def get_missions(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener todas las misiones de un juego, separadas por estado.

    Devuelve un diccionario con las listas `active`, `completed` y `failed`.
    """
    missions = db.query(Mission).filter(Mission.game_id == game_id).all()
    
    active = []
    completed = []
    failed = []
    
    for mission in missions:
        mission_data = {
            "id": mission.id,
            "mission_type": mission.mission_type,
            "origin_world": mission.origin_world,
            "execution_place": mission.execution_place,
            "max_date": mission.max_date,
            "result": mission.result,
            "created_date": mission.created_date,
            "completed_date": mission.completed_date,
            "notes": mission.notes
        }
        
        # Add type-specific fields
        if mission.mission_type == "campaign":
            mission_data["objective_number"] = mission.objective_number
        else:
            mission_data["mission_code"] = mission.mission_code
            mission_data["book_page"] = mission.book_page
        
        # Categorize by result
        if mission.result == "exito":
            completed.append(mission_data)
        elif mission.result == "fracaso":
            failed.append(mission_data)
        else:
            active.append(mission_data)
    
    return {
        "active": active,
        "completed": completed,
        "failed": failed,
        "total": len(missions)
    }


@router.post("/api/games/{game_id}/missions")
async def create_mission(
    game_id: str,
    mission_type: str = Form(...),
    origin_world: str = Form(""),
    execution_place: str = Form(...),
    max_date: str = Form(""),
    notes: str = Form(""),
    # Campaign-specific
    objective_number: Optional[int] = Form(None),
    # Special mission-specific
    mission_code: Optional[str] = Form(None),
    book_page: Optional[int] = Form(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Crear una nueva misión (objetivo de campaña o misión especial).

    Valida los campos requeridos según `mission_type` y programa un evento
    de fecha límite si se proporciona `max_date`.
    """
    from app.event_logger import EventLogger
    
    # Validate mission type
    if mission_type not in ["campaign", "special"]:
        raise HTTPException(status_code=400, detail="Mission type must be 'campaign' or 'special'")
    
    # Validate required fields for each type
    if mission_type == "campaign" and objective_number is None:
        raise HTTPException(status_code=400, detail="objective_number required for campaign missions")
    
    if mission_type == "special" and (not mission_code or book_page is None):
        raise HTTPException(status_code=400, detail="mission_code and book_page required for special missions")
    
    # Create mission
    mission = Mission(
        game_id=game_id,
        mission_type=mission_type,
        origin_world=origin_world,
        execution_place=execution_place,
        max_date=max_date,
        created_date=date.today().isoformat(),
        notes=notes,
        objective_number=objective_number,
        mission_code=mission_code,
        book_page=book_page
    )
    
    db.add(mission)
    db.commit()
    db.refresh(mission)
    
    # Log mission creation
    game = GameState(game_id)
    
    if mission_type == "campaign":
        mission_desc = f"Objetivo #{objective_number} de campaña"
    else:
        mission_desc = f"Misión especial {mission_code} (pág. {book_page})"
    
    EventLogger._log_to_game(
        game,
        f"🎯 Nueva misión: {mission_desc} en {execution_place}",
        event_type="info"
    )
    
    # Create mission deadline event if needed
    if max_date:
        game.state["event_queue"] = EventQueue.add_event(
            game.state.get("event_queue", []),
            "mission_deadline",
            max_date,
            {
                "mission_id": mission.id,
                "mission_type": mission_type,
                "objective": mission_desc
            }
        )
        game.save()
        
        EventLogger._log_to_game(
            game,
            f"📅 Fecha límite de misión programada: {max_date}",
            event_type="info"
        )
    
    return {
        "status": "success",
        "mission_id": mission.id,
        "mission_type": mission_type
    }


@router.put("/api/games/{game_id}/missions/{mission_id}")
async def update_mission_result(
    game_id: str,
    mission_id: int,
    result: str = Form(...),
    completed_date: str = Form(""),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Actualizar el resultado de una misión (marcar como éxito o fracaso)."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.game_id == game_id
    ).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if result not in ["exito", "fracaso", ""]:
        raise HTTPException(status_code=400, detail="Result must be 'exito', 'fracaso', or empty")
    
    mission.result = result
    if completed_date:
        mission.completed_date = completed_date
    if notes is not None:
        mission.notes = notes
    
    db.commit()
    
    return {
        "status": "success",
        "mission_id": mission.id,
        "result": result
    }


@router.post("/api/games/{game_id}/missions/{mission_id}/resolve")
async def resolve_mission_deadline(
    game_id: str,
    mission_id: int,
    success: bool = Form(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Resolver la fecha límite de una misión.

    `success` indica si la misión se considera completada con éxito o no.
    """
    from app.event_logger import EventLogger
    
    game = GameState(game_id)
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.game_id == game_id
    ).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Get current game date
    current_date = GameCalendar.date_to_string(
        game.state.get('year', 1),
        game.state.get('month', 1),
        game.state.get('day', 1)
    )
    
    # Update mission status
    mission.result = "exito" if success else "fracaso"
    mission.completed_date = current_date
    
    # Update reputation based on success
    if success:
        game.state["reputation"] = game.state.get("reputation", 0) + 1
    else:
        game.state["reputation"] = max(0, game.state.get("reputation", 0) - 1)
    
    # Remove mission_deadline event from queue
    game.state["event_queue"] = [
        e for e in game.state.get("event_queue", [])
        if not (e["type"] == "mission_deadline" and e["data"]["mission_id"] == mission_id)
    ]
    
    game.save()
    db.commit()
    
    # Log result
    if mission.mission_type == "campaign":
        mission_desc = f"Objetivo #{mission.objective_number}"
    else:
        mission_desc = f"Misión {mission.mission_code}"
    
    result_text = "completada con éxito ✅" if success else "fallida ❌"
    EventLogger._log_to_game(
        game,
        f"🎯 Misión {result_text}: {mission_desc}. Reputación: {game.state.get('reputation', 0)}",
        event_type="success" if success else "warning"
    )
    
    return {
        "status": "resolved",
        "success": success,
        "new_reputation": game.state.get("reputation", 0),
        "mission_result": mission.result
    }


@router.delete("/api/games/{game_id}/missions/{mission_id}")
async def delete_mission(
    game_id: str,
    mission_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Eliminar una misión de la base de datos."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.game_id == game_id
    ).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    db.delete(mission)
    db.commit()
    
    return {"status": "success", "deleted_id": mission_id}
