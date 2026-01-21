"""
Game state management with JSON persistence
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
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
            "ship_location_on_planet": "Mundo", # Mundo, Espaciopuerto, Instalación, Estación
            
            # Company & Ship
            "company_name": "Nueva Compañía",
            "ship_name": "Fénix Dorado",
            "ship_model": "Basic Starfall",
            "passengers": 0,
            
            # HUD - Critical Status
            "fuel": 18,
            "fuel_max": 30,
            "storage": 0,
            "storage_max": 40,
            "month": 1,
            "reputation": 0,
            
            # Calendar System (35 días/mes, 12 meses/año)
            "year": 1,
            "day": 1,  # month is already in HUD
            "event_queue": [],  # Cola ordenada de eventos [{type, date, data}]
            
            # Damage System
            "damages": {
                "light": False,
                "moderate": False,
                "severe": False,
                "counts": {
                    "light": 0,
                    "moderate": 0,
                    "severe": 0
                }
            },
            
            # Navigation
            "current_planet_code": None,
            "starting_planet_code": None,
            "current_area": None,  # Current area (can change during game)
            "explored_quadrants": [],  # List of explored coordinates
            "quadrant_planets": {},    # {"row,col": planet_code}
            "discovered_planets": {},  # {"planet_code": {"area": int, "quadrant": "row,col"}}
            
            # Difficulty & Treasury (set during setup)
            "difficulty": None,  # "easy", "normal", "hard"
            "treasury": 0,  # Saldo en Créditos Spacegom (SC)
            "reputation": 0,  # Reputación inicial
            
            # Transactions history
            "transactions": [],  # [{date, amount, description, category}]
            
            # Personnel managed in database (Personnel table)
            # Crew data is queried from DB, not stored in state
            
            # Trade
            "cargo": {},  # {product_code: quantity}
            
            # History / Events
            "events": [],
            "dice_rolls": [],
            
            # Action Flags
            "passenger_transport_available": True  # Reset on movement
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
    
    def get_adjacent_coordinates(self, row: int, col: int, jump_range: int = 1) -> List[Dict[str, Any]]:
        """
        Get all reachable coordinates within jump_range, 
        including area transitions (A <-> F).
        """
        reachable = []
        current_area = self.state.get("area")
        
        # Simple implementation for jump_range 1 for now
        # Standard grid movement (1-6 range)
        for dr in range(-jump_range, jump_range + 1):
            for dc in range(-jump_range, jump_range + 1):
                if dr == 0 and dc == 0:
                    continue
                
                target_r = row + dr
                target_c = col + dc
                target_area = current_area
                
                # Check column transitions
                if target_c < 1: # Left of Column A
                    if current_area > 2:
                        target_area = current_area - 1
                        target_c = 6 # Becomes Column F
                    else:
                        continue # Blocked (left of 2)
                elif target_c > 6: # Right of Column F
                    if current_area < 12:
                        target_area = current_area + 1
                        target_c = 1 # Becomes Column A
                    else:
                        continue # Blocked (right of 12)
                
                # Check row bounds (no row transitions between areas mentioned)
                if 1 <= target_r <= 6:
                    reachable.append({
                        "area": target_area,
                        "row": target_r,
                        "col": target_c,
                        "col_letter": chr(64 + target_c)
                    })
                    
        return reachable
    
    def update(self, **kwargs):
        """Update state fields"""
        for key, value in kwargs.items():
            if key in self.state:
                self.state[key] = value
        self.save()
    
    def add_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """Add event to history"""
        # Calculate current game date
        year = self.state.get('year', 1)
        month = self.state.get('month', 1)
        day = self.state.get('day', 1)
        game_date = f"{day:02d}-{month:02d}-{year}"

        event = {
            "timestamp": datetime.now().isoformat(),
            "game_date": game_date,
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
            
        # Reset movement-based flags
        self.state["passenger_transport_available"] = True
        self.save()
    
    def discover_planet(self, row: int, col: int, planet_code: int):
        """Record a planet discovery in a specific quadrant"""
        coord = f"{row},{col}"
        planet_code_str = str(planet_code)
        
        # Mapping for the quadrant
        self.state["quadrant_planets"][coord] = planet_code
        
        # Mapping for the world log (Hoja de Mundos)
        if planet_code_str not in self.state["discovered_planets"]:
            self.state["discovered_planets"][planet_code_str] = {
                "area": self.state.get("area"),
                "quadrant": coord
            }
        
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
