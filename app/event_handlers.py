"""
Sistema modular de handlers para eventos del juego Spacegom.

Cada tipo de evento tiene su propio handler que procesa lógica específica,
actualiza estado y decide si remover el evento de la cola.

Patrones de diseño utilizados:
    - Strategy Pattern: Cada evento tiene su propia estrategia de procesamiento
    - Command Pattern: Handlers encapsulan lógica compleja
    - Registry Pattern: Registro centralizado de handlers

Dependencias:
    - app.game_state: GameState para actualizar estado del juego
    - app.database: Personnel, Mission, EmployeeTask para queries
    - app.time_manager: GameCalendar, EventQueue para gestión temporal
    - app.event_logger: EventLogger para logging de eventos
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.game_state import GameState
from app.database import Personnel, Mission, EmployeeTask
from app.time_manager import GameCalendar, EventQueue
from app.event_logger import EventLogger
import json


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
    db: Session,
    manual_dice: Optional[str] = None
) -> EventHandlerResult:
    """
    Handler para procesar pago mensual de salarios (día 35).
    
    Este handler se ejecuta automáticamente cada día 35 del mes para procesar
    el pago de salarios de todo el personal activo.
    
    Acciones realizadas:
    1. Calcula total de salarios de personal activo
    2. Descuenta de tesorería en el estado del juego
    3. Registra transacción en el historial de transacciones
    4. Registra evento en el log del juego
    5. Crea siguiente evento de pago para el próximo mes (día 35)
    6. Marca el evento para ser removido de la cola
    
    Args:
        event: Diccionario con datos del evento (debe incluir "date")
        game: Instancia de GameState de la partida
        db: Sesión de base de datos SQLAlchemy
        manual_dice: No usado en este handler (mantenido por compatibilidad)
    
    Returns:
        EventHandlerResult con información del pago procesado
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
    event: Dict[str, Any],
    game: GameState,
    db: Session,
    manual_dice: Optional[str] = None
) -> EventHandlerResult:
    """
    Handler para completar búsqueda de contratación de personal.
    
    Este handler se ejecuta cuando llega la fecha de finalización de una
    búsqueda de contratación iniciada por el Director.
    
    Acciones realizadas:
    1. Obtiene la tarea y el empleado Director
    2. Calcula modificadores (experiencia, moral, reputación)
    3. Tira dados para determinar éxito (manual o automático)
    4. Determina éxito/fracaso comparando con umbral
    5. Si éxito: crea nuevo empleado en la base de datos
    6. Actualiza experiencia y moral del Director según resultado
    7. Registra evento en el log con detalles
    8. Inicia siguiente tarea en cola si existe
    9. Marca el evento para ser removido de la cola
    
    Args:
        event: Diccionario con datos del evento (debe incluir "data.task_id" y "date")
        game: Instancia de GameState de la partida
        db: Sesión de base de datos SQLAlchemy
        manual_dice: Opcional string con resultados manuales (ej: "4,6")
    
    Returns:
        EventHandlerResult con información detallada del resultado de la contratación
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
    event: Dict[str, Any],
    game: GameState,
    db: Session,
    manual_dice: Optional[str] = None
) -> EventHandlerResult:
    """
    Handler para fecha límite de misión.
    
    Este handler se ejecuta cuando llega la fecha límite de una misión.
    A diferencia de otros handlers, NO procesa automáticamente la misión,
    sino que retorna información para que el usuario tome una decisión.
    
    Acciones realizadas:
    1. Obtiene datos de la misión desde la base de datos
    2. Construye descripción de la misión según su tipo
    3. Retorna datos para mostrar modal al usuario
    4. NO borra el evento de la cola (espera resolución manual del usuario)
    
    Nota: El usuario debe llamar al endpoint de resolución de misión para
    completar el evento y marcarlo como resuelto.
    
    Args:
        event: Diccionario con datos del evento (debe incluir "data.mission_id")
        game: Instancia de GameState de la partida
        db: Sesión de base de datos SQLAlchemy
        manual_dice: No usado en este handler (mantenido por compatibilidad)
    
    Returns:
        EventHandlerResult con requires_user_input=True y datos de la misión
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

# Registro centralizado de handlers - mapea tipos de eventos a funciones handler
EVENT_HANDLERS: Dict[str, Callable] = {
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
