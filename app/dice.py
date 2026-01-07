"""
Dice rolling utilities for Spacegom
"""
import random
from typing import List, Tuple, Optional


class DiceRoller:
    """Handles dice rolling for the game"""
    
    @staticmethod
    def roll_dice(num_dice: int = 1, sides: int = 6) -> List[int]:
        """
        Roll multiple dice and return results in order
        
        Args:
            num_dice: Number of dice to roll
            sides: Number of sides per die (default 6)
        
        Returns:
            List of results in order
        """
        return [random.randint(1, sides) for _ in range(num_dice)]
    
    @staticmethod
    def roll_for_planet_code(manual_results: Optional[List[int]] = None) -> Tuple[int, List[int]]:
        """
        Roll 3 dice to generate a planet code (111-666)
        
        Args:
            manual_results: Optional list of 3 manual results
        
        Returns:
            Tuple of (code, dice_results)
        """
        if manual_results and len(manual_results) == 3:
            results = manual_results
        else:
            results = DiceRoller.roll_dice(num_dice=3, sides=6)
        
        # Compose code from individual dice (e.g., [4, 6, 6] -> 466)
        code = int(f"{results[0]}{results[1]}{results[2]}")
        
        return code, results
    
    @staticmethod
    def format_results(results: List[int]) -> str:
        """Format dice results for display"""
        return " + ".join(map(str, results))
    
    @staticmethod
    def results_to_code(results: List[int]) -> int:
        """Convert 3 dice results to planet code"""
        if len(results) != 3:
            raise ValueError("Need exactly 3 dice results for planet code")
        return int(f"{results[0]}{results[1]}{results[2]}")
    
    @staticmethod
    def world_density_from_roll(total: int) -> str:
        """
        Convert 2d6 total to world density level
        
        Args:
            total: Sum of 2d6 (2-12)
        
        Returns:
            "Baja" (2-4), "Media" (5-9), or "Alta" (10-12)
        """
        if total <= 4:
            return "Baja"
        elif total <= 9:
            return "Media"
        else:
            return "Alta"


class DiceHistoryEntry:
    """Represents a single dice roll in history"""
    
    def __init__(self, num_dice: int, results: List[int], is_manual: bool, purpose: str = ""):
        self.num_dice = num_dice
        self.results = results
        self.total = sum(results)
        self.is_manual = is_manual
        self.purpose = purpose
    
    def to_dict(self):
        return {
            "num_dice": self.num_dice,
            "results": self.results,
            "total": self.total,
            "is_manual": self.is_manual,
            "purpose": self.purpose
        }
