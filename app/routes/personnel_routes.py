"""
Routes para gestión de personal y sistema de contratación.

Este módulo contiene los endpoints relacionados con:
- CRUD de personal (Personnel)
- Sistema de contratación (hiring)
- Tareas de empleados (EmployeeTask)
"""
from fastapi import APIRouter, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json

from app.database import (
    get_db, Planet, Personnel, EmployeeTask, 
    POSITIONS_CATALOG, TECH_LEVEL_REQUIREMENTS
)
from app.game_state import GameState
from app.dice import DiceRoller
from app.time_manager import GameCalendar, EventQueue, calculate_hire_time, calculate_hire_salary

router = APIRouter(tags=["personnel"])


# ===== PERSONNEL CRUD =====

@router.get("/api/games/{game_id}/personnel")
async def get_personnel(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get all personnel for a game.
    
    Returns:
        List of active personnel with total monthly salaries.
    """
    personnel = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.is_active == True
    ).all()
    
    personnel_list = [{
        "id": p.id,
        "position": p.position,
        "name": p.name,
        "monthly_salary": p.monthly_salary,
        "experience": p.experience,
        "morale": p.morale,
        "hire_date": p.hire_date,
        "notes": p.notes
    } for p in personnel]
    
    total_monthly_salaries = sum(p.monthly_salary for p in personnel)
    
    return {
        "personnel": personnel_list,
        "total_monthly_salaries": total_monthly_salaries,
        "count": len(personnel)
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
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Contratar nuevo personal.

    Crea una fila `Personnel` y devuelve la información del empleado creado.
    """
    from datetime import date
    
    new_employee = Personnel(
        game_id=game_id,
        position=position,
        name=name,
        monthly_salary=monthly_salary,
        experience=experience,
        morale=morale,
        hire_date=date.today().isoformat(),
        is_active=True,
        notes=notes
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return {
        "status": "success",
        "employee": {
            "id": new_employee.id,
            "name": new_employee.name,
            "position": new_employee.position
        }
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
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Actualizar información de personal y persistir los cambios."""
    employee = db.query(Personnel).filter(
        Personnel.id == employee_id,
        Personnel.game_id == game_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if position is not None:
        employee.position = position
    if name is not None:
        employee.name = name
    if monthly_salary is not None:
        employee.monthly_salary = monthly_salary
    if experience is not None:
        employee.experience = experience
    if morale is not None:
        employee.morale = morale
    if notes is not None:
        employee.notes = notes
    
    db.commit()
    db.refresh(employee)
    
    return {"status": "success", "employee": {"id": employee.id, "name": employee.name}}


@router.delete("/api/games/{game_id}/personnel/{employee_id}")
async def fire_personnel(
    game_id: str,
    employee_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dar de baja a un empleado (marcar como inactivo)."""
    employee = db.query(Personnel).filter(
        Personnel.id == employee_id,
        Personnel.game_id == game_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.is_active = False
    db.commit()
    
    return {"status": "success", "message": f"{employee.name} has been dismissed"}


# ===== HIRING SYSTEM API =====

@router.get("/api/games/{game_id}/hire/available-positions")
async def get_available_positions(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener posiciones disponibles para contratación según el nivel tecnológico del planeta.

    Devuelve una lista de posiciones filtrada por `POSITIONS_CATALOG` y
    `TECH_LEVEL_REQUIREMENTS`.
    """
    game = GameState(game_id)
    current_planet_code = game.state.get("current_planet_code")
    
    if not current_planet_code:
        return {"positions": [], "error": "No current planet"}
    
    # Get planet tech level
    planet = db.query(Planet).filter(Planet.code == current_planet_code).first()
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
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Iniciar búsqueda de contratación para el Director Gerente.

    Valida la petición, crea una `EmployeeTask` y programa su finalización
    si queda en primera posición de la cola.
    """
    from app.event_logger import EventLogger
    
    # Validate position exists
    if position not in POSITIONS_CATALOG:
        raise HTTPException(status_code=400, detail="Invalid position")
    
    # Validate experience level
    if experience_level not in ["Novato", "Estándar", "Veterano"]:
        raise HTTPException(status_code=400, detail="Invalid experience level")
    
    # Get Director Gerente
    director = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.position == "Director gerente",
        Personnel.is_active == True
    ).first()
    
    if not director:
        raise HTTPException(status_code=404, detail="Director Gerente not found")
    
    # Calculate search days
    position_data = POSITIONS_CATALOG[position]
    
    # Process manual dice if provided
    if manual_dice_days:
        try:
            days_dice = [int(x.strip()) for x in manual_dice_days.split(',')]
            if len(days_dice) != 2:
                raise ValueError("Se requieren 2 dados")
            if any(d < 1 or d > 6 for d in days_dice):
                raise ValueError("Dados deben estar entre 1 y 6")
        
            # Apply experience modifier
            exp_mod = {'Novato': -1, 'Estándar': 0, 'Veterano': 1}.get(experience_level, 0)
            search_days = sum(days_dice) + exp_mod
            search_days = max(1, search_days)  # Minimum 1 day
        except ValueError as e:
            raise HTTPException(400, f"Dados inválidos: {str(e)}")
    else:
        # Automatic fallback
        dice_roller = DiceRoller()
        search_days = calculate_hire_time(
            position_data["search_time_dice"],
            experience_level,
            dice_roller
        )
    
    # Calculate salary
    final_salary = calculate_hire_salary(position_data["base_salary"], experience_level)
    
    # Determine queue position
    existing_tasks = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game_id,
        EmployeeTask.employee_id == director.id,
        EmployeeTask.status.in_(["pending", "in_progress"])
    ).count()
    
    queue_position = existing_tasks + 1
    
    # Get current date
    game = GameState(game_id)
    current_date = GameCalendar.date_to_string(
        game.state.get('year', 1),
        game.state.get('month', 1),
        game.state.get('day', 1)
    )
    
    # Create task
    task = EmployeeTask(
        game_id=game_id,
        employee_id=director.id,
        task_type="hire_search",
        status="pending",
        queue_position=queue_position,
        task_data=json.dumps({
            "position": position,
            "experience_level": experience_level,
            "search_days": search_days,
            "base_salary": position_data["base_salary"],
            "final_salary": final_salary,
            "hire_threshold": position_data["hire_threshold"]
        }),
        created_date=current_date
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Log event for ALL hire searches
    EventLogger._log_to_game(game, EventLogger.format_hire_start(position, experience_level, search_days))
    
    # If it's the first task, start it immediately
    if queue_position == 1:
        task.status = "in_progress"
        task.started_date = current_date
        task.completion_date = GameCalendar.add_days(current_date, search_days)
        
        # Add event to queue
        game.state["event_queue"] = EventQueue.add_event(
            game.state.get("event_queue", []),
            "task_completion",
            task.completion_date,
            {"task_id": task.id, "employee_id": director.id}
        )
        game.save()
        db.commit()
    
    return {
        "status": "success",
        "task_id": task.id,
        "queue_position": queue_position,
        "search_days": search_days,
        "final_salary": final_salary,
        "task_status": task.status
    }


@router.get("/api/games/{game_id}/personnel/{employee_id}/tasks")
async def get_employee_tasks(
    game_id: str,
    employee_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Obtener todas las tareas de un empleado (principalmente Director Gerente)."""
    
    employee = db.query(Personnel).filter(
        Personnel.id == employee_id,
        Personnel.game_id == game_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    tasks = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game_id,
        EmployeeTask.employee_id == employee_id
    ).order_by(EmployeeTask.queue_position).all()
    
    current_task = None
    pending_tasks = []
    completed_tasks = []
    
    for task in tasks:
        task_data = json.loads(task.task_data) if task.task_data else {}
        
        task_info = {
            "id": task.id,
            "task_type": task.task_type,
            "status": task.status,
            "queue_position": task.queue_position,
            "task_data": task_data,
            "created_date": task.created_date,
            "started_date": task.started_date,
            "completion_date": task.completion_date,
            "finished_date": task.finished_date
        }
        
        if task.status == "in_progress":
            current_task = task_info
        elif task.status == "pending":
            pending_tasks.append(task_info)
        elif task.status in ["completed", "failed"]:
            result_data = json.loads(task.result_data) if task.result_data else {}
            task_info["result"] = result_data
            completed_tasks.append(task_info)
    
    return {
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "position": employee.position
        },
        "current_task": current_task,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "total_tasks": len(tasks)
    }


@router.put("/api/games/{game_id}/tasks/{task_id}/reorder")
async def reorder_task(
    game_id: str,
    task_id: int,
    new_position: int = Form(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Reordenar una tarea pendiente en la cola; ajusta las posiciones de las demás."""
    
    task = db.query(EmployeeTask).filter(
        EmployeeTask.id == task_id,
        EmployeeTask.game_id == game_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "pending":
        raise HTTPException(status_code=400, detail="Can only reorder pending tasks")
    
    # Get all pending tasks for this employee
    pending_tasks = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game_id,
        EmployeeTask.employee_id == task.employee_id,
        EmployeeTask.status == "pending"
    ).order_by(EmployeeTask.queue_position).all()
    
    # Validate new position
    if new_position < 2 or new_position > len(pending_tasks) + 1:
        raise HTTPException(status_code=400, detail="Invalid new position")
    
    old_position = task.queue_position
    
    # Reorder tasks
    if old_position < new_position:
        # Moving down
        for t in pending_tasks:
            if old_position < t.queue_position <= new_position:
                t.queue_position -= 1
    else:
        # Moving up
        for t in pending_tasks:
            if new_position <= t.queue_position < old_position:
                t.queue_position += 1
    
    task.queue_position = new_position
    db.commit()
    
    return {"status": "success", "new_position": new_position}


@router.delete("/api/games/{game_id}/tasks/{task_id}")
async def delete_task(
    game_id: str,
    task_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Eliminar una tarea pendiente y ajustar la cola en consecuencia."""
    
    task = db.query(EmployeeTask).filter(
        EmployeeTask.id == task_id,
        EmployeeTask.game_id == game_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "pending":
        raise HTTPException(status_code=400, detail="Can only delete pending tasks")
    
    employee_id = task.employee_id
    deleted_position = task.queue_position
    
    db.delete(task)
    
    # Adjust queue positions of remaining tasks
    remaining_tasks = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game_id,
        EmployeeTask.employee_id == employee_id,
        EmployeeTask.status == "pending",
        EmployeeTask.queue_position > deleted_position
    ).all()
    
    for t in remaining_tasks:
        t.queue_position -= 1
    
    db.commit()
    
    return {"status": "success", "deleted_id": task_id}
