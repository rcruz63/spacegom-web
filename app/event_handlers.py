"""
Sistema de handlers para eventos del juego Spacegom

Cada tipo de evento tiene su propio handler que:
1. Procesa la lógica específica del evento
2. Actualiza el estado del juego
3. Registra logs
4. Retorna si el evento debe borrarse de la cola

Patrón: Strategy/Command para escalabilidad
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.game_state import GameState
from app.database import Personnel, Mission, EmployeeTask
from app.time_manager import GameCalendar, EventQueue
from app.event_logger import EventLogger
import json


class EventHandlerResult:
    """Resultado de un event handler"""
    def __init__(
        self,
        success: bool = True,
        remove_from_queue: bool = True,
        requires_user_input: bool = False,
        event_data: Dict[str, Any] = None
    ):
        self.success = success
        self.remove_from_queue = remove_from_queue
        self.requires_user_input = requires_user_input
        self.event_data = event_data or {}
    
    def to_dict(self):
        return {
            "success": self.success,
            "remove_from_queue": self.remove_from_queue,
            "requires_user_input": self.requires_user_input,
            **self.event_data
        }


# ============================================================================
# EVENT HANDLERS
# ============================================================================

def handle_salary_payment(
    event: Dict,
    game: GameState,
    db: Session,
    manual_dice: Optional[str] = None
) -> EventHandlerResult:
    """
    Handler para pago mensual de salarios (día 35)
    
    Acciones:
    1. Calcular total de salarios de personal activo
    2. Descontar de tesorería (game state)
    3. Registrar transacción en game state
    4. Logging del evento
    5. Crear siguiente evento de pago (próximo mes día 35)
    6. Borrar evento actual de la cola
    """
    game_id = game.game_id
    
    # 1. Calcular total de salarios
    active_personnel = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.is_active == True
    ).all()
    
    total_salary = sum(p.monthly_salary for p in active_personnel)
    
    # 2. Descontar de tesorería (en game state)
    old_balance = game.state.get("treasury", 0)
    new_balance = old_balance - total_salary
    game.state["treasury"] = new_balance
    
    # 3. Registrar transacción en game state
    if "transactions" not in game.state:
        game.state["transactions"] = []
    
    transaction = {
        "date": event["date"],
        "type": "expense",
        "category": "salaries",
        "amount": total_salary,
        "description": f"Pago mensual de salarios - {len(active_personnel)} empleados"
    }
    game.state["transactions"].append(transaction)
    
    # 4. Logging
    EventLogger._log_to_game(
        game,
        f"💸 Pago de salarios: {total_salary} SC para {len(active_personnel)} empleados. Saldo: {old_balance} → {new_balance} SC",
        event_type="info"
    )
    
    # 5. Crear siguiente evento de pago
    next_salary_date = GameCalendar.next_day_35(event["date"])
    game.state["event_queue"] = EventQueue.add_event(
        game.state.get("event_queue", []),
        "salary_payment",
        next_salary_date,
        {"monthly_payment": True}
    )
    game.save()
    
    # 6. Retornar resultado (se borrará automáticamente)
    return EventHandlerResult(
        success=True,
        remove_from_queue=True,
        event_data={
            "type": "salary_payment",
            "total_paid": total_salary,
            "employees_count": len(active_personnel),
            "old_balance": old_balance,
            "new_balance": new_balance
        }
    )


def handle_task_completion(
    event: Dict,
    game: GameState,
    db: Session,
    manual_dice: Optional[str] = None
) -> EventHandlerResult:
    """
    Handler para completar búsqueda de personal
    
    Acciones:
    1. Obtener tarea y empleado (Director)
    2. Calcular modificadores
    3. Tirar dados (manual o automático)
    4. Determinar éxito/fracaso
    5. Si éxito: crear nuevo empleado
    6. Actualizar experiencia/moral del Director
    7. Logging
    8. Iniciar siguiente tarea en cola si existe
    9. Borrar evento de la cola
    """
    from app.dice import DiceRoller
    
    task_id = event["data"]["task_id"]
    task = db.query(EmployeeTask).get(task_id)
    
    if not task or task.status != "in_progress":
        return EventHandlerResult(
            success=False,
            remove_from_queue=True,
            event_data={"error": "Task not found or not in progress"}
        )
    
    task_data = json.loads(task.task_data)
    director = db.query(Personnel).get(task.employee_id)
    
    # Calculate modifiers
    exp_mod = {"N": -1, "E": 0, "V": 1}.get(director.experience, 0)
    morale_mod = {"B": -1, "M": 0, "A": 1}.get(director.morale, 0)
    rep_mod = game.state.get("reputation", 0)
    total_mod = exp_mod + morale_mod + rep_mod
    
    # Roll dice
    if manual_dice:
        dice_values = [int(x) for x in manual_dice.split(',')]
    else:
        dice_roller = DiceRoller()
        dice_values = dice_roller.roll_dice(2, 6)
    
    dice_sum = sum(dice_values)
    final_result = dice_sum + total_mod
    threshold = task_data["hire_threshold"]
    success = final_result >= threshold
    
    # Update director's morale and experience
    from app.personnel_manager import update_employee_roll_stats
    stats_changes = update_employee_roll_stats(director, dice_values, final_result)
    
    # Log detailed stats changes if any
    for msg in stats_changes["messages"]:
        EventLogger._log_to_game(game, f"👔 Director: {msg}", event_type="info")
    
    new_employee_id = None
    if success:
        # Create new employee
        from app.name_suggestions import get_random_personal_name
        
        new_employee = Personnel(
            game_id=game.game_id,
            position=task_data["position"],
            name=get_random_personal_name(),
            monthly_salary=task_data["final_salary"],
            experience=task_data["experience_level"][0],
            morale="M",
            hire_date=event["date"],
            is_active=True,
            notes="Contratado automáticamente"
        )
        db.add(new_employee)
        db.flush()
        new_employee_id = new_employee.id
        
        # Log success
        EventLogger._log_to_game(
            game,
            EventLogger.format_hire_success(
                task_data["position"],
                new_employee.name,
                task_data["final_salary"]
            ),
            event_type="success"
        )
    else:
        # Log failure
        EventLogger._log_to_game(
            game,
            EventLogger.format_hire_failure(
                task_data["position"],
                task_data["experience_level"]
            ),
            event_type="warning"
        )
    
    # Update task
    task.status = "completed" if success else "failed"
    task.finished_date = event["date"]
    task.result_data = json.dumps({
        "dice_values": dice_values,
        "dice_sum": dice_sum,
        "modifiers": {
            "experience": exp_mod,
            "morale": morale_mod,
            "reputation": rep_mod,
            "total": total_mod
        },
        "final_result": final_result,
        "threshold": threshold,
        "success": success,
        "employee_id": new_employee_id
    })
    
    # Start next task in queue if exists
    next_task = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game.game_id,
        EmployeeTask.employee_id == director.id,
        EmployeeTask.status == "pending"
    ).order_by(EmployeeTask.queue_position).first()
    
    next_task_started = None
    if next_task:
        next_task.status = "in_progress"
        next_task.started_date = event["date"]
        next_task_data = json.loads(next_task.task_data)
        completion_date = GameCalendar.add_days(event["date"], next_task_data["search_days"])
        next_task.completion_date = completion_date
        
        # Add event for next task
        game.state["event_queue"] = EventQueue.add_event(
            game.state.get("event_queue", []),
            "task_completion",
            completion_date,
            {"task_id": next_task.id, "employee_id": director.id}
        )
        game.save()
        
        next_task_started = {
            "position": next_task_data["position"],
            "completion_date": completion_date
        }
    
    return EventHandlerResult(
        success=True,
        remove_from_queue=True,
        event_data={
            "type": "hire_resolution",
            "position": task_data["position"],
            "experience_level": task_data["experience_level"],
            "dice": dice_values,
            "modifiers": {
                "experience": exp_mod,
                "morale": morale_mod,
                "reputation": rep_mod,
                "total": total_mod
            },
            "total": final_result,
            "threshold": threshold,
            "success": success,
            "new_employee_id": new_employee_id,
            "next_task_started": next_task_started
        }
    )


def handle_mission_deadline(
    event: Dict,
    game: GameState,
    db: Session,
    manual_dice: Optional[str] = None
) -> EventHandlerResult:
    """
    Handler para fecha límite de misión
    
    Acciones:
    1. Obtener datos de la misión
    2. Retornar datos para mostrar modal al usuario
    3. NO borrar evento (espera resolución del usuario)
    
    Nota: El usuario debe llamar a /resolve_mission para completar
    """
    mission_id = event["data"]["mission_id"]
    mission = db.query(Mission).get(mission_id)
    
    if not mission:
        return EventHandlerResult(
            success=False,
            remove_from_queue=True,
            event_data={"error": "Mission not found"}
        )
    
    # Build mission description based on type
    if mission.mission_type == "campaign":
        mission_desc = f"Objetivo #{mission.objective_number}"
    else:
        mission_desc = f"Misión {mission.mission_code} (pág. {mission.book_page})"
    
    return EventHandlerResult(
        success=True,
        remove_from_queue=False,  # NO borrar hasta que usuario resuelva
        requires_user_input=True,
        event_data={
            "type": "mission_deadline",
            "mission_id": mission_id,
            "mission_type": mission.mission_type,
            "objective": mission_desc,  # Descripción construida
            "execution_place": mission.execution_place or "",
            "notes": mission.notes or ""
        }
    )


# ============================================================================
# HANDLER REGISTRY
# ============================================================================

EVENT_HANDLERS = {
    "salary_payment": handle_salary_payment,
    "task_completion": handle_task_completion,
    "mission_deadline": handle_mission_deadline
}


def get_event_handler(event_type: str):
    """
    Obtiene el handler para un tipo de evento
    
    Args:
        event_type: Tipo de evento
        
    Returns:
        Función handler o None si no existe
    """
    return EVENT_HANDLERS.get(event_type)
