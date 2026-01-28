"""
Módulo de gestión de personal para Spacegom.

Maneja la lógica de actualización de empleados, incluyendo evolución de Moral
y Experiencia según las reglas del juego.

Las reglas están basadas en REGLAS_MORAL_EXPERIENCIA.md:
- Moral: Aumenta con resultado >= 10, disminuye con resultado <= 4
- Experiencia: Aumenta con doble 6 natural (6, 6) en tirada de dados

Acepta empleado como dict (DynamoDB/GameState) o objeto con .morale/.experience.
"""
from typing import List, Dict, Any, Tuple, Union

# Niveles de moral: Baja, Media, Alta
MORAL_LEVELS: List[str] = ["B", "M", "A"]
# Mapeo de nivel a índice para facilitar incremento/decremento
MORAL_MAP: Dict[str, int] = {level: i for i, level in enumerate(MORAL_LEVELS)}

# Niveles de experiencia: Novato, Experto, Veterano
EXP_LEVELS: List[str] = ["N", "E", "V"]
# Mapeo de nivel a índice para facilitar incremento/decremento
EXP_MAP: Dict[str, int] = {level: i for i, level in enumerate(EXP_LEVELS)}

def update_employee_roll_stats(
    employee: Union[Dict[str, Any], Any],
    dice_values: List[int],
    final_result: int,
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
        employee: Dict o objeto con morale/experience (se muta in-place)
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
    def _get(e: Any, k: str, default: str = "M") -> str:
        return e.get(k, default) if isinstance(e, dict) else getattr(e, k, default)

    def _set(e: Any, k: str, v: str) -> None:
        if isinstance(e, dict):
            e[k] = v
        else:
            setattr(e, k, v)

    old_m = _get(employee, "morale", "M")
    old_x = _get(employee, "experience", "N")
    changes = {
        "moral_change": 0,
        "xp_change": 0,
        "old_moral": old_m,
        "new_moral": old_m,
        "old_xp": old_x,
        "new_xp": old_x,
        "messages": [],
    }

    current_moral_idx = MORAL_MAP.get(old_m, 1)
    new_moral_idx = current_moral_idx

    if final_result <= 4:
        if new_moral_idx > 0:
            new_moral_idx -= 1
            changes["moral_change"] = -1
            changes["messages"].append("Moral disminuye por resultado bajo (<= 4).")
    elif final_result >= 10:
        if new_moral_idx < 2:
            new_moral_idx += 1
            changes["moral_change"] = 1
            changes["messages"].append("Moral aumenta por buen resultado (>= 10).")

    if new_moral_idx != current_moral_idx:
        _set(employee, "morale", MORAL_LEVELS[new_moral_idx])
        changes["new_moral"] = MORAL_LEVELS[new_moral_idx]

    is_double_six = len(dice_values) == 2 and dice_values[0] == 6 and dice_values[1] == 6
    if is_double_six:
        current_xp_idx = EXP_MAP.get(old_x, 0)
        if current_xp_idx < 2:
            current_xp_idx += 1
            changes["xp_change"] = 1
            _set(employee, "experience", EXP_LEVELS[current_xp_idx])
            changes["new_xp"] = EXP_LEVELS[current_xp_idx]
            changes["messages"].append("¡Experiencia aumenta por Doble 6 natural!")

    return changes
