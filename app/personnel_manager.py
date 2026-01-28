"""
Módulo de gestión de personal para Spacegom.

Maneja la lógica de actualización de empleados, incluyendo evolución de Moral
y Experiencia según las reglas del juego.

Las reglas están basadas en REGLAS_MORAL_EXPERIENCIA.md:
- Moral: Aumenta con resultado >= 10, disminuye con resultado <= 4
- Experiencia: Aumenta con doble 6 natural (6, 6) en tirada de dados

Dependencias:
    - app.database.Personnel: Modelo de empleado de la base de datos
"""
from typing import List, Dict, Any, Tuple
from app.database import Personnel

# Niveles de moral: Baja, Media, Alta
MORAL_LEVELS: List[str] = ["B", "M", "A"]
# Mapeo de nivel a índice para facilitar incremento/decremento
MORAL_MAP: Dict[str, int] = {level: i for i, level in enumerate(MORAL_LEVELS)}

# Niveles de experiencia: Novato, Experto, Veterano
EXP_LEVELS: List[str] = ["N", "E", "V"]
# Mapeo de nivel a índice para facilitar incremento/decremento
EXP_MAP: Dict[str, int] = {level: i for i, level in enumerate(EXP_LEVELS)}

def update_employee_roll_stats(
    employee: Personnel, 
    dice_values: List[int], 
    final_result: int
) -> Dict[str, Any]:
    """
    Actualiza Moral y Experiencia de un empleado basado en resultado de tirada.
    
    Aplica las reglas del juego para evolución de estadísticas:
    
    Reglas de Moral:
        - Pérdida: Resultado final <= 4 (disminuye un nivel)
        - Ganancia: Resultado final >= 10 (aumenta un nivel)
        - Sin cambio: Resultado entre 5-9
    
    Reglas de Experiencia:
        - Ganancia: Doble 6 natural (6, 6) en los dados (aumenta un nivel)
        - Sin cambio: Cualquier otra combinación
    
    La función es idempotente y puede llamarse múltiples veces sin efectos
    secundarios no deseados. Valida límites de niveles antes de aplicar cambios.
    
    Args:
        employee: Instancia del modelo Personnel a actualizar
        dice_values: Lista de valores individuales de los dados (ej: [4, 6])
        final_result: Resultado total incluyendo modificadores (Suma + Mods)
    
    Returns:
        Diccionario con detalles de los cambios realizados:
        {
            "moral_change": int,      # -1, 0, o 1
            "xp_change": int,         # 0 o 1
            "old_moral": str,         # Nivel anterior ("B", "M", "A")
            "new_moral": str,         # Nivel nuevo
            "old_xp": str,            # Nivel anterior ("N", "E", "V")
            "new_xp": str,            # Nivel nuevo
            "messages": List[str]     # Mensajes descriptivos de cambios
        }
    
    Example:
        >>> employee.morale = "M"
        >>> employee.experience = "N"
        >>> result = update_employee_roll_stats(employee, [6, 6], 12)
        >>> result["moral_change"]
        1  # Aumentó moral por resultado >= 10
        >>> result["xp_change"]
        1  # Aumentó experiencia por doble 6
        >>> employee.morale
        'A'
        >>> employee.experience
        'E'
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
    
    # --- REGLAS DE MORAL ---
    # Ganancia: Total >= 10
    # Pérdida: Total <= 4
    
    current_moral_idx = MORAL_MAP.get(employee.morale, 1)  # Por defecto M si desconocido
    new_moral_idx = current_moral_idx
    
    if final_result <= 4:
        # Pérdida de moral por resultado bajo
        if new_moral_idx > 0:  # Verificar que no esté ya en el mínimo
            new_moral_idx -= 1
            changes["moral_change"] = -1
            changes["messages"].append("Moral disminuye por resultado bajo (<= 4).")
    elif final_result >= 10:
        # Ganancia de moral por buen resultado
        if new_moral_idx < 2:  # Verificar que no esté ya en el máximo
            new_moral_idx += 1
            changes["moral_change"] = 1
            changes["messages"].append("Moral aumenta por buen resultado (>= 10).")
            
    # Aplicar cambio de moral si hubo modificación
    if new_moral_idx != current_moral_idx:
        employee.morale = MORAL_LEVELS[new_moral_idx]
        changes["new_moral"] = employee.morale

    # --- REGLAS DE EXPERIENCIA ---
    # Ganancia: Doble 6 natural (6, 6) en los dados
    
    is_double_six = len(dice_values) == 2 and dice_values[0] == 6 and dice_values[1] == 6
    
    if is_double_six:
        current_xp_idx = EXP_MAP.get(employee.experience, 0)  # Por defecto N
        if current_xp_idx < 2:  # Verificar que no esté ya en el máximo (Veterano)
            current_xp_idx += 1
            changes["xp_change"] = 1
            employee.experience = EXP_LEVELS[current_xp_idx]
            changes["new_xp"] = employee.experience
            changes["messages"].append("¡Experiencia aumenta por Doble 6 natural!")
            
    return changes
