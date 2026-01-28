"""
Módulo de logging centralizado para eventos del juego Spacegom.

Proporciona funcionalidad simple y centralizada para registrar eventos del juego.
Los eventos se almacenan en el estado del juego y se muestran en la página de logs.

Uso:
    from app.event_logger import EventLogger
    
    logger = EventLogger(game_id)
    logger.log("Iniciada búsqueda de Piloto Novato, tardará 2 días")
    logger.log("Contratado Asistente de vuelo por 150 SC/mes", "success")

Dependencias:
    - app.game_state: GameState para almacenar eventos
    - datetime: Para timestamps de eventos
"""

from app.game_state import GameState
from datetime import datetime
from typing import List, Dict, Any, Optional


class EventLogger:
    """
    Logger centralizado para eventos del juego.
    
    Almacena eventos en el estado del juego con fecha del juego, timestamp real,
    mensaje y tipo. Los eventos se pueden filtrar y recuperar para mostrar en
    la interfaz de usuario.
    
    Tipos de eventos soportados:
        - "info": Información general
        - "success": Acción exitosa
        - "warning": Advertencia
        - "error": Error o fallo
    """
    
    def __init__(self, game_id: str):
        """
        Inicializa el logger para una partida específica.
        
        Args:
            game_id: Identificador único de la partida
        """
        self.game_id = game_id
        self.game = GameState(game_id)
    
    def log(self, message: str, event_type: str = "info") -> None:
        """
        Registra un evento en el log del juego.
        
        Crea una entrada de log con fecha del juego, timestamp real, mensaje
        y tipo. La entrada se añade al array "event_logs" en el estado del juego
        y se guarda automáticamente.
        
        Args:
            message: Mensaje descriptivo del evento
            event_type: Tipo de evento ("info", "success", "warning", "error")
        
        Example:
            >>> logger = EventLogger("game_123")
            >>> logger.log("Iniciada búsqueda de Piloto Novato, tardará 2 días")
            >>> logger.log("Contratado Asistente de vuelo por 150 SC/mes", "success")
        """
        # Get current game date
        year = self.game.state.get('year', 1)
        month = self.game.state.get('month', 1)
        day = self.game.state.get('day', 1)
        game_date = f"{day:02d}-{month:02d}-{year}"
        
        # Get current real timestamp
        timestamp = datetime.now().isoformat()
        
        # Create event entry
        event = {
            "game_date": game_date,
            "timestamp": timestamp,
            "message": message,
            "type": event_type
        }
        
        # Initialize logs array if it doesn't exist
        if "event_logs" not in self.game.state:
            self.game.state["event_logs"] = []
        
        # Add event to logs
        self.game.state["event_logs"].append(event)
        
        # Save game state
        self.game.save()
    
    def get_logs(self, limit: Optional[int] = None, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera logs del juego con filtros opcionales.
        
        Los logs se retornan en orden inverso (más recientes primero) y pueden
        filtrarse por tipo de evento y limitarse en cantidad.
        
        Args:
            limit: Número máximo de logs a retornar (None = todos)
            event_type: Filtrar por tipo de evento ("info", "success", "warning", "error")
        
        Returns:
            Lista de diccionarios con eventos, cada uno contiene:
            {
                "game_date": str,      # Fecha del juego (dd-mm-yy)
                "timestamp": str,       # Timestamp ISO real
                "message": str,         # Mensaje del evento
                "type": str            # Tipo de evento
            }
        """
        logs = self.game.state.get("event_logs", [])
        
        # Filter by type if specified
        if event_type:
            logs = [log for log in logs if log.get("type") == event_type]
        
        # Reverse to show most recent first
        logs = list(reversed(logs))
        
        # Apply limit if specified
        if limit:
            logs = logs[:limit]
        
        return logs
    
    def clear_logs(self) -> None:
        """
        Limpia todos los logs del juego (usar con precaución).
        
        Elimina permanentemente todos los eventos registrados. Esta acción
        no se puede deshacer.
        """
        self.game.state["event_logs"] = []
        self.game.save()
    
    @staticmethod
    def _log_to_game(game: GameState, message: str, event_type: str = "info") -> None:
        """
        Loggea evento a una instancia existente de GameState.
        
        Método estático útil cuando ya se tiene una instancia de GameState
        y se quiere evitar crear una nueva instancia solo para logging.
        Más eficiente que crear un EventLogger nuevo.
        
        Args:
            game: Instancia existente de GameState
            message: Mensaje descriptivo del evento
            event_type: Tipo de evento ("info", "success", "warning", "error")
        """
        # Get current game date
        year = game.state.get('year', 1)
        month = game.state.get('month', 1)
        day = game.state.get('day', 1)
        game_date = f"{day:02d}-{month:02d}-{year}"
        
        # Get current real timestamp
        timestamp = datetime.now().isoformat()
        
        # Create event entry
        event = {
            "game_date": game_date,
            "timestamp": timestamp,
            "message": message,
            "type": event_type
        }
        
        # Initialize logs array if it doesn't exist
        if "event_logs" not in game.state:
            game.state["event_logs"] = []
        
        # Add event to logs
        game.state["event_logs"].append(event)
        
        # Save game state
        game.save()
    
    # Funciones helper de formato - Proporcionan mensajes consistentes para eventos comunes
    
    @staticmethod
    def format_hire_start(position: str, experience: str, days: int) -> str:
        """
        Formatea mensaje de inicio de búsqueda de contratación.
        
        Args:
            position: Puesto a contratar (ej: "Piloto")
            experience: Nivel de experiencia (ej: "Novato")
            days: Días que tardará la búsqueda
        
        Returns:
            Mensaje formateado (ej: "Iniciada búsqueda de Piloto Novato, tardará 2 días")
        """
        return f"Iniciada búsqueda de {position} {experience}, tardará {days} días"
    
    @staticmethod
    def format_hire_success(position: str, name: str, salary: int) -> str:
        """
        Formatea mensaje de contratación exitosa.
        
        Args:
            position: Puesto contratado
            name: Nombre del empleado contratado
            salary: Salario mensual en SC
        
        Returns:
            Mensaje formateado (ej: "Contratado Piloto: Juan Pérez por 150 SC/mes")
        """
        return f"Contratado {position}: {name} por {salary} SC/mes"
    
    @staticmethod
    def format_hire_failure(position: str, experience: str) -> str:
        """
        Formatea mensaje de fallo en contratación.
        
        Args:
            position: Puesto que se intentó contratar
            experience: Nivel de experiencia buscado
        
        Returns:
            Mensaje formateado (ej: "Fallo en la búsqueda de Piloto Novato")
        """
        return f"Fallo en la búsqueda de {position} {experience}"
    
    @staticmethod
    def format_salary_payment(total: int, balance: int) -> str:
        """
        Formatea mensaje de pago de salarios.
        
        Args:
            total: Total pagado en SC
            balance: Saldo resultante en tesorería
        
        Returns:
            Mensaje formateado (ej: "Se pagan salarios por un total de 500 SC, saldo resultante: 1000 SC")
        """
        return f"Se pagan salarios por un total de {total} SC, saldo resultante: {balance} SC"
    
    @staticmethod
    def format_fire(position: str, name: str) -> str:
        """
        Formatea mensaje de despido de empleado.
        
        Args:
            position: Puesto del empleado
            name: Nombre del empleado
        
        Returns:
            Mensaje formateado (ej: "Despedido Piloto: Juan Pérez")
        """
        return f"Despedido {position}: {name}"
    
    @staticmethod
    def format_mission_start(mission_type: str, objective: str) -> str:
        """
        Formatea mensaje de inicio de misión.
        
        Args:
            mission_type: Tipo de misión (ej: "campaign", "special")
            objective: Objetivo o descripción de la misión
        
        Returns:
            Mensaje formateado (ej: "Iniciada misión campaign: Objetivo #1")
        """
        return f"Iniciada misión {mission_type}: {objective}"
    
    @staticmethod
    def format_mission_complete(mission_type: str, objective: str, result: str) -> str:
        """
        Formatea mensaje de completación de misión.
        
        Args:
            mission_type: Tipo de misión
            objective: Objetivo de la misión
            result: Resultado ("exito" o "fracaso")
        
        Returns:
            Mensaje formateado (ej: "Misión completada con éxito: Objetivo #1")
        """
        result_text = "éxito" if result == "exito" else "fracaso"
        return f"Misión completada con {result_text}: {objective}"
