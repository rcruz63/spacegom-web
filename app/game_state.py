"""
Game state management with JSON persistence
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class GameState:
    """Manages game state with JSON persistence"""
    
    GAMES_DIR = "data/games"
    
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.game_dir = Path(self.GAMES_DIR) / game_id
        self.state_file = self.game_dir / "state.json"
        self.state = self._load_or_create_state()
    
    def _load_or_create_state(self) -> Dict[str, Any]:
        """Load existing state or create new one"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create new game state
            return self._create_default_state()
    
    def _create_default_state(self) -> Dict[str, Any]:
        """Create default game state"""
        return {
            "game_id": self.game_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            
            # Initial Setup
            "area": None,  # Space area (2-12 from 2d6)
            "world_density": None,  # "Baja", "Media", "Alta"
            "setup_complete": False,
            "ship_row": None,  # 1-6
            "ship_col": None,  # 1-6
            "ship_pos_complete": False,
            
            # HUD - Critical Status
            "fuel": 18,
            "fuel_max": 30,
            "storage": 16,
            "storage_max": 40,
            "month": 1,
            "reputation": 0,
            
            # Damage System
            "damages": {
                "light": False,
                "moderate": False,
                "severe": False
            },
            
            # Navigation
            "current_planet_code": None,
            "current_area": None,  # Current area (can change during game)
            "explored_quadrants": [],  # List of explored coordinates
            
            # Crew
            "crew": [
                {
                    "id": 1,
                    "name": "Elena Voss",
                    "position": "PILOTO",
                    "salary": 1200,
                    "experience": "VETERANA",
                    "morale": 2  # 0=Baja, 1=Media, 2=Alta
                },
                {
                    "id": 2,
                    "name": "Marcus Chen",
                    "position": "INGENIERO",
                    "salary": 950,
                    "experience": "ESTÁNDAR",
                    "morale": 2
                },
                {
                    "id": 3,
                    "name": "Zara Kaine",
                    "position": "NEGOCIADORA",
                    "salary": 800,
                    "experience": "NOVATA",
                    "morale": 0
                }
            ],
            "health_level": "MEDIA",
            
            # Finance
            "credits": 45230,
            "weekly_expenses": {
                "salaries": 2950,
                "maintenance": 500
            },
            "monthly_loans": {
                "galactic_bank": 5000,
                "ship_upgrades": 2000
            },
            
            # Trade
            "cargo": {},  # {product_code: quantity}
            
            # History / Events
            "events": [],
            "dice_rolls": []
        }
    
    def save(self):
        """Save current state to JSON"""
        # Ensure directory exists
        self.game_dir.mkdir(parents=True, exist_ok=True)
        
        # Update timestamp
        self.state["updated_at"] = datetime.now().isoformat()
        
        # Write to file
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def update(self, **kwargs):
        """Update state fields"""
        for key, value in kwargs.items():
            if key in self.state:
                self.state[key] = value
        self.save()
    
    def add_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """Add event to history"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "data": data or {}
        }
        self.state["events"].append(event)
        self.save()
    
    def record_dice_roll(self, num_dice: int, results: list, is_manual: bool, purpose: str = ""):
        """Record dice roll in history"""
        roll = {
            "timestamp": datetime.now().isoformat(),
            "num_dice": num_dice,
            "results": results,
            "total": sum(results),
            "is_manual": is_manual,
            "purpose": purpose
        }
        self.state["dice_rolls"].append(roll)
        self.save()
        return roll
    
    def explore_quadrant(self, row: int, col: int):
        """Mark a quadrant as explored"""
        coord = f"{row},{col}"
        if coord not in self.state["explored_quadrants"]:
            self.state["explored_quadrants"].append(coord)
            self.save()
    
    def is_quadrant_explored(self, row: int, col: int) -> bool:
        """Check if quadrant is explored"""
        coord = f"{row},{col}"
        return coord in self.state["explored_quadrants"]
    
    @classmethod
    def list_games(cls) -> list:
        """List all available games"""
        games_path = Path(cls.GAMES_DIR)
        if not games_path.exists():
            return []
        
        games = []
        for game_dir in games_path.iterdir():
            if game_dir.is_dir():
                state_file = game_dir / "state.json"
                if state_file.exists():
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        games.append({
                            "game_id": game_dir.name,
                            "created_at": state.get("created_at"),
                            "updated_at": state.get("updated_at"),
                            "month": state.get("month", 1),
                            "credits": state.get("credits", 0)
                        })
        
        return sorted(games, key=lambda x: x["updated_at"], reverse=True)
    
    @classmethod
    def create_new_game(cls, game_name: Optional[str] = None) -> "GameState":
        """Create a new game"""
        if not game_name:
            game_name = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Clean game name (remove invalid chars)
        game_id = "".join(c for c in game_name if c.isalnum() or c in ('_', '-')).lower()
        
        return cls(game_id)
