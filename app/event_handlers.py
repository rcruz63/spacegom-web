"""
Sistema modular de handlers para eventos del juego Spacegom.

Handlers usan GameState (DynamoDB); sin dependencia de SQL/db.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional

from app.game_state import GameState
from app.time_manager import GameCalendar, EventQueue
from app.event_logger import EventLogger


class EventHandlerResult:
    """
    Resultado estandarizado de un event handler.
    
    Encapsula la información sobre el resultado del procesamiento de un evento,
    incluyendo si fue exitoso, si debe removerse de la cola, y si requiere
    interacción del usuario.
    
    Attributes:
        success: True si el handler se ejecutó correctamente
        remove_from_queue: True si el evento debe borrarse de la cola
        requires_user_input: True si requiere interacción del usuario
        event_data: Diccionario con datos adicionales del resultado
    """
    def __init__(
        self,
        success: bool = True,
        remove_from_queue: bool = True,
        requires_user_input: bool = False,
        event_data: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa el resultado de un handler.
        
        Args:
            success: Si el handler se ejecutó correctamente
            remove_from_queue: Si el evento debe borrarse de la cola
            requires_user_input: Si requiere interacción del usuario
            event_data: Datos adicionales del resultado
        """
        self.success = success
        self.remove_from_queue = remove_from_queue
        self.requires_user_input = requires_user_input
        self.event_data = event_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna representación diccionario para serialización.
        
        Útil para respuestas API o logging.
        
        Returns:
            Diccionario con todos los atributos del resultado
        """
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
    event: Dict[str, Any],
    game: GameState,
    manual_dice: Optional[str] = None,
) -> EventHandlerResult:
    """Procesa pago mensual de salarios (día 35)."""
    active_personnel = game.get_personnel(active_only=True)
    total_salary = sum(p["monthly_salary"] for p in active_personnel)

    old_balance = game.state.get("treasury", 0)
    new_balance = old_balance - total_salary
    game.state["treasury"] = new_balance

    transaction = {
        "date": event["date"],
        "type": "expense",
        "category": "salaries",
        "amount": total_salary,
        "description": f"Pago mensual de salarios - {len(active_personnel)} empleados",
    }
    game.append_transaction(transaction)

    EventLogger._log_to_game(
        game,
        f"💸 Pago de salarios: {total_salary} SC para {len(active_personnel)} empleados. Saldo: {old_balance} → {new_balance} SC",
        event_type="info",
    )

    next_salary_date = GameCalendar.next_day_35(event["date"])
    game.state["event_queue"] = EventQueue.add_event(
        game.state.get("event_queue", []),
        "salary_payment",
        next_salary_date,
        {"monthly_payment": True},
    )
    game.save()

    return EventHandlerResult(
        success=True,
        remove_from_queue=True,
        event_data={
            "type": "salary_payment",
            "total_paid": total_salary,
            "employees_count": len(active_personnel),
            "old_balance": old_balance,
            "new_balance": new_balance,
        },
    )


def handle_task_completion(
    event: Dict[str, Any],
    game: GameState,
    manual_dice: Optional[str] = None,
) -> EventHandlerResult:
    """Completa búsqueda de contratación: tira dados, crea empleado si éxito, actualiza director."""
    from app.dice import DiceRoller
    from app.name_suggestions import get_random_personal_name
    from app.personnel_manager import update_employee_roll_stats

    task_id = event["data"]["task_id"]
    task = game.get_task_by_id(task_id)
    if not task or task.get("status") != "in_progress":
        return EventHandlerResult(
            success=False,
            remove_from_queue=True,
            event_data={"error": "Task not found or not in progress"},
        )

    task_data = json.loads(task["task_data"]) if isinstance(task.get("task_data"), str) else (task.get("task_data") or {})
    director = game.get_personnel_by_id(task["employee_id"])
    if not director:
        return EventHandlerResult(success=False, remove_from_queue=True, event_data={"error": "Director not found"})

    exp_mod = {"N": -1, "E": 0, "V": 1}.get(director.get("experience", "N"), 0)
    morale_mod = {"B": -1, "M": 0, "A": 1}.get(director.get("morale", "M"), 0)
    rep_mod = game.state.get("reputation", 0)
    total_mod = exp_mod + morale_mod + rep_mod

    if manual_dice:
        dice_values = [int(x.strip()) for x in manual_dice.split(",")]
    else:
        dice_values = DiceRoller().roll_dice(2, 6)
    dice_sum = sum(dice_values)
    final_result = dice_sum + total_mod
    threshold = task_data.get("hire_threshold", 7)
    success = final_result >= threshold

    stats_changes = update_employee_roll_stats(director, dice_values, final_result)
    game.update_personnel(director["id"], {"morale": director["morale"], "experience": director["experience"]})
    for msg in stats_changes["messages"]:
        EventLogger._log_to_game(game, f"👔 Director: {msg}", event_type="info")

    new_employee_id = None
    if success:
        name = get_random_personal_name()
        new_employee_id = game.add_personnel({
            "position": task_data["position"],
            "name": name,
            "monthly_salary": task_data["final_salary"],
            "experience": (task_data.get("experience_level") or "Estándar")[0],
            "morale": "M",
            "hire_date": event["date"],
            "is_active": True,
            "notes": "Contratado automáticamente",
        })
        EventLogger._log_to_game(
            game,
            EventLogger.format_hire_success(task_data["position"], name, task_data["final_salary"]),
            event_type="success",
        )
    else:
        EventLogger._log_to_game(
            game,
            EventLogger.format_hire_failure(task_data["position"], task_data.get("experience_level", "")),
            event_type="warning",
        )

    result_data = {
        "dice_values": dice_values,
        "dice_sum": dice_sum,
        "modifiers": {"experience": exp_mod, "morale": morale_mod, "reputation": rep_mod, "total": total_mod},
        "final_result": final_result,
        "threshold": threshold,
        "success": success,
        "employee_id": new_employee_id,
    }
    game.update_task(task_id, {"status": "completed" if success else "failed", "finished_date": event["date"], "result_data": json.dumps(result_data)})

    pending = [t for t in game.get_employee_tasks(employee_id=director["id"]) if t.get("status") == "pending"]
    pending.sort(key=lambda t: t.get("queue_position", 0))
    next_task = pending[0] if pending else None
    next_task_started = None
    if next_task:
        nd = json.loads(next_task["task_data"]) if isinstance(next_task.get("task_data"), str) else (next_task.get("task_data") or {})
        completion_date = GameCalendar.add_days(event["date"], nd.get("search_days", 1))
        game.update_task(next_task["id"], {"status": "in_progress", "started_date": event["date"], "completion_date": completion_date})
        game.state["event_queue"] = EventQueue.add_event(
            game.state.get("event_queue", []),
            "task_completion",
            completion_date,
            {"task_id": next_task["id"], "employee_id": director["id"]},
        )
        game.save()
        next_task_started = {"position": nd.get("position"), "completion_date": completion_date}

    return EventHandlerResult(
        success=True,
        remove_from_queue=True,
        event_data={
            "type": "hire_resolution",
            "position": task_data["position"],
            "experience_level": task_data.get("experience_level", ""),
            "dice": dice_values,
            "modifiers": {"experience": exp_mod, "morale": morale_mod, "reputation": rep_mod, "total": total_mod},
            "total": final_result,
            "threshold": threshold,
            "success": success,
            "new_employee_id": new_employee_id,
            "next_task_started": next_task_started,
        },
    )


def handle_mission_deadline(
    event: Dict[str, Any],
    game: GameState,
    manual_dice: Optional[str] = None,
) -> EventHandlerResult:
    """Fecha límite de misión: retorna datos para modal; no borra evento hasta resolución."""
    mission_id = event["data"]["mission_id"]
    mission = game.get_mission_by_id(mission_id)
    if not mission:
        return EventHandlerResult(
            success=False,
            remove_from_queue=True,
            event_data={"error": "Mission not found"},
        )
    if mission.get("mission_type") == "campaign":
        mission_desc = f"Objetivo #{mission.get('objective_number')}"
    else:
        mission_desc = f"Misión {mission.get('mission_code')} (pág. {mission.get('book_page')})"
    return EventHandlerResult(
        success=True,
        remove_from_queue=False,
        requires_user_input=True,
        event_data={
            "type": "mission_deadline",
            "mission_id": mission_id,
            "mission_type": mission.get("mission_type"),
            "objective": mission_desc,
            "execution_place": mission.get("execution_place") or "",
            "notes": mission.get("notes") or "",
        },
    )


# ============================================================================
# HANDLER REGISTRY
# ============================================================================

EVENT_HANDLERS: Dict[str, Callable[..., EventHandlerResult]] = {
    "salary_payment": handle_salary_payment,
    "task_completion": handle_task_completion,
    "mission_deadline": handle_mission_deadline
}


def get_event_handler(event_type: str) -> Optional[Callable]:
    """
    Obtiene el handler apropiado para un tipo de evento.
    
    Usa el registro centralizado EVENT_HANDLERS para encontrar la función
    handler correspondiente al tipo de evento.
    
    Args:
        event_type: Tipo de evento (ej: "salary_payment", "task_completion")
    
    Returns:
        Función handler correspondiente o None si no existe el tipo
    
    Example:
        >>> handler = get_event_handler("salary_payment")
        >>> result = handler(event, game, db)
    """
    return EVENT_HANDLERS.get(event_type)
