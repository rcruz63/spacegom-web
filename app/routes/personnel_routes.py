"""
Routes para gestión de personal y sistema de contratación.

CRUD de personal y tareas de empleados vía GameState (DynamoDB).
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, Form, HTTPException

from app.database import POSITIONS_CATALOG, TECH_LEVEL_REQUIREMENTS
from app.planets_repo import get_planet_by_code
from app.game_state import GameState
from app.dice import DiceRoller
from app.time_manager import GameCalendar, EventQueue, calculate_hire_time, calculate_hire_salary

router = APIRouter(tags=["personnel"])


# ===== PERSONNEL CRUD =====

@router.get("/api/games/{game_id}/personnel")
async def get_personnel(game_id: str) -> Dict[str, Any]:
    """Obtiene todo el personal activo de una partida."""
    game = GameState(game_id)
    personnel = game.get_personnel(active_only=True)
    personnel_list = [
        {
            "id": p["id"],
            "position": p["position"],
            "name": p["name"],
            "monthly_salary": p["monthly_salary"],
            "experience": p["experience"],
            "morale": p["morale"],
            "hire_date": p.get("hire_date"),
            "notes": p.get("notes", ""),
        }
        for p in personnel
    ]
    total_monthly_salaries = sum(p["monthly_salary"] for p in personnel)
    return {
        "personnel": personnel_list,
        "total_monthly_salaries": total_monthly_salaries,
        "count": len(personnel),
    }


@router.post("/api/games/{game_id}/personnel")
async def hire_personnel(
    game_id: str,
    position: str = Form(...),
    name: str = Form(...),
    monthly_salary: int = Form(...),
    experience: str = Form(...),
    morale: str = Form(...),
    notes: str = Form(""),
) -> Dict[str, Any]:
    """Contrata nuevo personal directamente (sin proceso de búsqueda)."""
    from datetime import date

    game = GameState(game_id)
    uid = game.add_personnel({
        "position": position,
        "name": name,
        "monthly_salary": monthly_salary,
        "experience": experience,
        "morale": morale,
        "hire_date": date.today().isoformat(),
        "is_active": True,
        "notes": notes,
    })
    return {
        "status": "success",
        "employee": {"id": uid, "name": name, "position": position},
    }


@router.put("/api/games/{game_id}/personnel/{employee_id}")
async def update_personnel(
    game_id: str,
    employee_id: int,
    position: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    monthly_salary: Optional[int] = Form(None),
    experience: Optional[str] = Form(None),
    morale: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
) -> Dict[str, Any]:
    """Actualizar información de personal y persistir los cambios."""
    game = GameState(game_id)
    employee = game.get_personnel_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    updates = {}
    if position is not None:
        updates["position"] = position
    if name is not None:
        updates["name"] = name
    if monthly_salary is not None:
        updates["monthly_salary"] = monthly_salary
    if experience is not None:
        updates["experience"] = experience
    if morale is not None:
        updates["morale"] = morale
    if notes is not None:
        updates["notes"] = notes
    if updates:
        game.update_personnel(employee_id, updates)
    return {"status": "success", "employee": {"id": employee_id, "name": updates.get("name", employee["name"])}}


@router.delete("/api/games/{game_id}/personnel/{employee_id}")
async def fire_personnel(game_id: str, employee_id: int) -> Dict[str, Any]:
    """Dar de baja a un empleado (marcar como inactivo)."""
    game = GameState(game_id)
    employee = game.get_personnel_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    game.update_personnel(employee_id, {"is_active": False})
    return {"status": "success", "message": f"{employee['name']} has been dismissed"}


# ===== HIRING SYSTEM API =====

@router.get("/api/games/{game_id}/hire/available-positions")
async def get_available_positions(game_id: str) -> Dict[str, Any]:
    """Obtener posiciones disponibles para contratación según el nivel tecnológico del planeta.

    Devuelve una lista de posiciones filtrada por `POSITIONS_CATALOG` y
    `TECH_LEVEL_REQUIREMENTS`.
    """
    game = GameState(game_id)
    current_planet_code = game.state.get("current_planet_code")
    
    if not current_planet_code:
        return {"positions": [], "error": "No current planet"}
    
    planet = get_planet_by_code(current_planet_code)
    if not planet or not planet.tech_level:
        return {"positions": [], "error": "Planet tech level not defined"}
    
    # Filter positions by tech level
    available = []
    for position_name, position_data in POSITIONS_CATALOG.items():
        required_level = position_data["tech_level"]
        if planet.tech_level in TECH_LEVEL_REQUIREMENTS.get(required_level, []):
            available.append({
                "name": position_name,
                "search_time_dice": position_data["search_time_dice"],
                "base_salary": position_data["base_salary"],
                "hire_threshold": position_data["hire_threshold"],
                "tech_level": required_level
            })
    
    return {
        "planet_code": current_planet_code,
        "planet_tech_level": planet.tech_level,
        "positions": available
    }


@router.post("/api/games/{game_id}/hire/start")
async def start_hire_search(
    game_id: str,
    position: str = Form(...),
    experience_level: str = Form(...),
    manual_dice_days: Optional[str] = Form(None),
) -> Dict[str, Any]:
    """Iniciar búsqueda de contratación para el Director Gerente."""
    from app.event_logger import EventLogger

    if position not in POSITIONS_CATALOG:
        raise HTTPException(status_code=400, detail="Invalid position")
    if experience_level not in ["Novato", "Estándar", "Veterano"]:
        raise HTTPException(status_code=400, detail="Invalid experience level")

    game = GameState(game_id)
    personnel = game.get_personnel(active_only=True)
    director = next((p for p in personnel if p.get("position") == "Director gerente"), None)
    if not director:
        raise HTTPException(status_code=404, detail="Director Gerente not found")

    position_data = POSITIONS_CATALOG[position]
    if manual_dice_days:
        try:
            days_dice = [int(x.strip()) for x in manual_dice_days.split(",")]
            if len(days_dice) != 2:
                raise ValueError("Se requieren 2 dados")
            if any(d < 1 or d > 6 for d in days_dice):
                raise ValueError("Dados deben estar entre 1 y 6")
            exp_mod = {"Novato": -1, "Estándar": 0, "Veterano": 1}.get(experience_level, 0)
            search_days = max(1, sum(days_dice) + exp_mod)
        except ValueError as e:
            raise HTTPException(400, f"Dados inválidos: {str(e)}") from e
    else:
        search_days = calculate_hire_time(
            position_data["search_time_dice"],
            experience_level,
            DiceRoller(),
        )
    final_salary = calculate_hire_salary(position_data["base_salary"], experience_level)

    tasks = game.get_employee_tasks(employee_id=director["id"])
    active = [t for t in tasks if t.get("status") in ("pending", "in_progress")]
    queue_position = len(active) + 1

    current_date = GameCalendar.date_to_string(
        game.state.get("year", 1),
        game.state.get("month", 1),
        game.state.get("day", 1),
    )
    task_data = {
        "position": position,
        "experience_level": experience_level,
        "search_days": search_days,
        "base_salary": position_data["base_salary"],
        "final_salary": final_salary,
        "hire_threshold": position_data["hire_threshold"],
    }
    task_id = game.add_task({
        "employee_id": director["id"],
        "task_type": "hire_search",
        "status": "pending",
        "queue_position": queue_position,
        "task_data": json.dumps(task_data),
        "created_date": current_date,
    })

    EventLogger._log_to_game(game, EventLogger.format_hire_start(position, experience_level, search_days))

    if queue_position == 1:
        completion_date = GameCalendar.add_days(current_date, search_days)
        game.update_task(task_id, {
            "status": "in_progress",
            "started_date": current_date,
            "completion_date": completion_date,
        })
        game.state["event_queue"] = EventQueue.add_event(
            game.state.get("event_queue", []),
            "task_completion",
            completion_date,
            {"task_id": task_id, "employee_id": director["id"]},
        )
        game.save()

    return {
        "status": "success",
        "task_id": task_id,
        "queue_position": queue_position,
        "search_days": search_days,
        "final_salary": final_salary,
        "task_status": "in_progress" if queue_position == 1 else "pending",
    }


@router.get("/api/games/{game_id}/personnel/{employee_id}/tasks")
async def get_employee_tasks(game_id: str, employee_id: int) -> Dict[str, Any]:
    """Obtener todas las tareas de un empleado (principalmente Director Gerente)."""
    game = GameState(game_id)
    employee = game.get_personnel_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tasks = game.get_employee_tasks(employee_id=employee_id)
    tasks.sort(key=lambda t: (t.get("queue_position", 0), t.get("id", 0)))

    current_task = None
    pending_tasks = []
    completed_tasks = []
    for t in tasks:
        td = json.loads(t["task_data"]) if isinstance(t.get("task_data"), str) else (t.get("task_data") or {})
        task_info = {
            "id": t["id"],
            "task_type": t.get("task_type"),
            "status": t.get("status"),
            "queue_position": t.get("queue_position"),
            "task_data": td,
            "created_date": t.get("created_date"),
            "started_date": t.get("started_date"),
            "completion_date": t.get("completion_date"),
            "finished_date": t.get("finished_date"),
        }
        if t.get("status") == "in_progress":
            current_task = task_info
        elif t.get("status") == "pending":
            pending_tasks.append(task_info)
        elif t.get("status") in ("completed", "failed"):
            rd = t.get("result_data")
            task_info["result"] = json.loads(rd) if isinstance(rd, str) else (rd or {})
            completed_tasks.append(task_info)

    return {
        "employee": {"id": employee["id"], "name": employee["name"], "position": employee["position"]},
        "current_task": current_task,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "total_tasks": len(tasks),
    }


@router.put("/api/games/{game_id}/tasks/{task_id}/reorder")
async def reorder_task(
    game_id: str,
    task_id: int,
    new_position: int = Form(...),
) -> Dict[str, Any]:
    """Reordenar una tarea pendiente en la cola; ajusta las posiciones de las demás."""
    game = GameState(game_id)
    task = game.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.get("status") != "pending":
        raise HTTPException(status_code=400, detail="Can only reorder pending tasks")

    pending = [t for t in game.get_employee_tasks(employee_id=task["employee_id"]) if t.get("status") == "pending"]
    pending.sort(key=lambda t: t.get("queue_position", 0))
    if new_position < 2 or new_position > len(pending) + 1:
        raise HTTPException(status_code=400, detail="Invalid new position")

    old_position = task["queue_position"]
    if old_position < new_position:
        for t in pending:
            q = t.get("queue_position", 0)
            if old_position < q <= new_position:
                game.update_task(t["id"], {"queue_position": q - 1})
    else:
        for t in pending:
            q = t.get("queue_position", 0)
            if new_position <= q < old_position:
                game.update_task(t["id"], {"queue_position": q + 1})
    game.update_task(task_id, {"queue_position": new_position})
    return {"status": "success", "new_position": new_position}


@router.delete("/api/games/{game_id}/tasks/{task_id}")
async def delete_task(game_id: str, task_id: int) -> Dict[str, Any]:
    """Eliminar una tarea pendiente y ajustar la cola en consecuencia."""
    game = GameState(game_id)
    task = game.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.get("status") != "pending":
        raise HTTPException(status_code=400, detail="Can only delete pending tasks")

    employee_id = task["employee_id"]
    deleted_position = task["queue_position"]
    game.delete_task(task_id)

    for t in game.get_employee_tasks(employee_id=employee_id):
        if t.get("status") != "pending":
            continue
        if t.get("queue_position", 0) > deleted_position:
            game.update_task(t["id"], {"queue_position": t["queue_position"] - 1})
    return {"status": "success", "deleted_id": task_id}
