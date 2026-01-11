"""
Event Logger Module for Spacegom

Provides simple, centralized logging functionality for game events.
Events are stored in the game_state and displayed in the logs page.

Usage:
    from app.event_logger import EventLogger
    
    logger = EventLogger(game_id)
    logger.log("Iniciada búsqueda de Piloto Novato, tardará 2 días")
    logger.log("Contratado Asistente de vuelo por 150 SC/mes")
"""

from app.game_state import GameState
from datetime import datetime


class EventLogger:
    """Simple event logger for game events"""
    
    def __init__(self, game_id: str):
        """
        Initialize logger for a specific game
        
        Args:
            game_id: ID of the game to log events for
        """
        self.game_id = game_id
        self.game = GameState(game_id)
    
    def log(self, message: str, event_type: str = "info"):
        """
        Register an event in the game log
        
        Args:
            message: Descriptive message of the event
            event_type: Type of event (info, success, warning, error)
        
        Example:
            logger.log("Iniciada búsqueda de Piloto Novato, tardará 2 días")
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
    
    def get_logs(self, limit: int = None, event_type: str = None):
        """
        Retrieve game logs
        
        Args:
            limit: Maximum number of logs to return (most recent first)
            event_type: Filter by event type (optional)
        
        Returns:
            List of event dictionaries
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
    
    def clear_logs(self):
        """Clear all logs for this game (use with caution)"""
        self.game.state["event_logs"] = []
        self.game.save()
    
    @staticmethod
    def _log_to_game(game: GameState, message: str, event_type: str = "info"):
        """
        Log event to an existing GameState instance (avoids creating new instance)
        
        Args:
            game: Existing GameState instance
            message: Descriptive message of the event
            event_type: Type of event (info, success, warning, error)
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
    
    @staticmethod
    def format_hire_start(position: str, experience: str, days: int):
        """Helper to format hire search start message"""
        return f"Iniciada búsqueda de {position} {experience}, tardará {days} días"
    
    @staticmethod
    def format_hire_success(position: str, name: str, salary: int):
        """Helper to format successful hire message"""
        return f"Contratado {position}: {name} por {salary} SC/mes"
    
    @staticmethod
    def format_hire_failure(position: str, experience: str):
        """Helper to format failed hire message"""
        return f"Fallo en la búsqueda de {position} {experience}"
    
    @staticmethod
    def format_salary_payment(total: int, balance: int):
        """Helper to format salary payment message"""
        return f"Se pagan salarios por un total de {total} SC, saldo resultante: {balance} SC"
    
    @staticmethod
    def format_fire(position: str, name: str):
        """Helper to format employee dismissal message"""
        return f"Despedido {position}: {name}"
    
    @staticmethod
    def format_mission_start(mission_type: str, objective: str):
        """Helper to format mission start message"""
        return f"Iniciada misión {mission_type}: {objective}"
    
    @staticmethod
    def format_mission_complete(mission_type: str, objective: str, result: str):
        """Helper to format mission completion message"""
        result_text = "éxito" if result == "exito" else "fracaso"
        return f"Misión completada con {result_text}: {objective}"
