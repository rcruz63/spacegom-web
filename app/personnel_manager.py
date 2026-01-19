"""
Personnel Manager Module

Handles logic for employee updates, including Moral and Experience evolution rules.
Refer to REGLAS_MORAL_EXPERIENCIA.md for rule definitions.
"""
from typing import List, Dict, Any, Tuple
from app.database import Personnel

# Moral progression map
MORAL_LEVELS = ["B", "M", "A"]
MORAL_MAP = {level: i for i, level in enumerate(MORAL_LEVELS)}

# Experience progression map
EXP_LEVELS = ["N", "E", "V"]
EXP_MAP = {level: i for i, level in enumerate(EXP_LEVELS)}

def update_employee_roll_stats(
    employee: Personnel, 
    dice_values: List[int], 
    final_result: int
) -> Dict[str, Any]:
    """
    Updates an employee's Moral and Experience based on a dice roll action.
    
    Args:
        employee: The Personnel model instance.
        dice_values: List of raw dice values (e.g., [6, 6]).
        final_result: Total result including modifiers (Sum + Mods).
        
    Returns:
        Dict with details about what changed.
    """
    changes = {
        "moral_change": 0,
        "xp_change": 0,
        "old_moral": employee.morale,
        "new_moral": employee.morale,
        "old_xp": employee.experience,
        "new_xp": employee.experience,
        "messages": []
    }
    
    # --- MORAL RULES ---
    # Gain: Total >= 10
    # Loss: Total <= 4
    
    current_moral_idx = MORAL_MAP.get(employee.morale, 1) # Default to M if unknown
    new_moral_idx = current_moral_idx
    
    if final_result <= 4:
        # Loss
        if new_moral_idx > 0:
            new_moral_idx -= 1
            changes["moral_change"] = -1
            changes["messages"].append("Moral disminuye por resultado bajo (<= 4).")
    elif final_result >= 10:
        # Gain
        if new_moral_idx < 2:
            new_moral_idx += 1
            changes["moral_change"] = 1
            changes["messages"].append("Moral aumenta por buen resultado (>= 10).")
            
    # Apply Moral Change
    if new_moral_idx != current_moral_idx:
        employee.morale = MORAL_LEVELS[new_moral_idx]
        changes["new_moral"] = employee.morale

    # --- EXPERIENCE RULES ---
    # Gain: Natural double 6 (6, 6)
    
    is_double_six = len(dice_values) == 2 and dice_values[0] == 6 and dice_values[1] == 6
    
    if is_double_six:
        current_xp_idx = EXP_MAP.get(employee.experience, 0) # Default N
        if current_xp_idx < 2:
            current_xp_idx += 1
            changes["xp_change"] = 1
            employee.experience = EXP_LEVELS[current_xp_idx]
            changes["new_xp"] = employee.experience
            changes["messages"].append("¡Experiencia aumenta por Doble 6 natural!")
            
    return changes
