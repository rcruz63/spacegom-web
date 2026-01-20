# personnel_manager.py - Gestión de Personal

## Overview

Módulo para manejar lógica de actualización de empleados, incluyendo evolución de Moral y Experiencia según reglas del juego.

**Ubicación**: `app/personnel_manager.py`
**Líneas**: ~110
**Dependencias**: `database` (Personnel)

## Constantes

### MORAL_LEVELS = ["B", "M", "A"]
Niveles de moral: Baja, Media, Alta

### EXP_LEVELS = ["N", "E", "V"]
Niveles de experiencia: Novato, Experto, Veterano

### MORAL_MAP y EXP_MAP
Diccionarios para conversión nivel ↔ índice

## Función update_employee_roll_stats(employee: Personnel, dice_values: List[int], final_result: int) -> Dict[str, Any]

Actualiza Moral y Experiencia de un empleado basado en resultado de tirada.

### Reglas de Moral
- **Pérdida**: Resultado final ≤ 4
- **Ganancia**: Resultado final ≥ 10

### Reglas de Experiencia
- **Ganancia**: Doble 6 natural (6, 6)

### Retorno
Diccionario con cambios realizados y mensajes descriptivos.

## Dependencias

- **Personnel**: Modelo de empleado de database.py

## Notas de Implementación

- **Reglas del Juego**: Basado en REGLAS_MORAL_EXPERIENCIA.md
- **Validación**: Verifica límites de niveles
- **Mensajes**: Proporciona feedback detallado de cambios
- **Idempotente**: Puede llamarse múltiples veces sin efectos secundarios

## Mejores Prácticas

- Usar después de cada tirada relevante
- Mostrar mensajes al usuario
- Validar employee existe antes de llamar
- Mantener consistencia con reglas del manual