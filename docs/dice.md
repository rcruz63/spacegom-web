# dice.py - Utilidades de Tiradas de Dados

## Overview

Este módulo proporciona utilidades para todas las mecánicas de dados del juego Spacegom. Maneja tiradas automáticas y manuales, generación de códigos de planetas, y conversión de resultados.

**Ubicación**: `app/dice.py`
**Líneas**: ~150
**Dependencias**: `random`, `typing`

## Clase DiceRoller

### Métodos Estáticos

#### `roll_dice(num_dice: int = 1, sides: int = 6) -> List[int]`
Tira múltiples dados y retorna resultados en orden.

#### `roll_for_planet_code(manual_results: Optional[List[int]] = None) -> Tuple[int, List[int]]`
Genera código de planeta tirando 3d6 (111-666).

#### `format_results(results: List[int]) -> str`
Formatea resultados para display ("4 + 6 + 6").

#### `results_to_code(results: List[int]) -> int`
Convierte lista de 3 resultados a código de planeta.

#### `world_density_from_roll(total: int) -> str`
Convierte total de 2d6 a nivel de densidad de mundos:
- 2-4: "Baja"
- 5-9: "Media"
- 10-12: "Alta"

#### `get_next_planet_code(code: int) -> int`
Obtiene siguiente código válido en secuencia 3d6 para búsqueda consecutiva de planetas.

## Clase DiceHistoryEntry

### Propósito
Representa una entrada individual en el historial de tiradas.

### Atributos
- `num_dice`: Número de dados tirados
- `results`: Lista de resultados individuales
- `total`: Suma total
- `is_manual`: Si fue tirada manual
- `purpose`: Propósito de la tirada

### Método `to_dict()`
Retorna representación diccionario para serialización.

## Dependencias

- **random**: Generación de números aleatorios
- **typing**: Type hints

## Notas de Implementación

- **Secuencia 3d6**: Implementa lógica de incremento manual (111→112→...→121→...)
- **Validación**: Verifica límites de dados (1-6)
- **Flexibilidad**: Soporta dados con diferentes números de caras
- **Historial**: Integración con sistema de logging de GameState

## Mejores Prácticas

- Usar `manual_results` para testing determinístico
- Validar longitud de listas antes de procesar
- Mantener consistencia en formato de códigos de planeta
- Documentar propósito de tiradas para debugging