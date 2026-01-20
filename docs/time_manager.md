# time_manager.py - Gestión del Tiempo y Calendario

## Overview

Sistema completo de gestión temporal para el juego Spacegom. Maneja calendario, operaciones con fechas y cola de eventos ordenados.

**Ubicación**: `app/time_manager.py`
**Líneas**: 333
**Dependencias**: `math`, `typing`

## Clase GameCalendar

### Constantes
- `DAYS_PER_MONTH = 35`
- `MONTHS_PER_YEAR = 12`

### Métodos Estáticos

#### parse_date(date_str: str) -> Tuple[int, int, int]
Convierte string "dd-mm-yy" a tupla (año, mes, día)

#### date_to_string(year: int, month: int, day: int) -> str
Convierte tupla a string "dd-mm-yy"

#### add_days(date_str: str, days: int) -> str
Añade días a fecha, manejando overflow de meses/años

#### subtract_days(date_str: str, days: int) -> str
Resta días a fecha, manejando underflow

#### compare_dates(date1: str, date2: str) -> int
Compara dos fechas (-1, 0, 1)

#### is_day_35(date_str: str) -> bool
Verifica si es día 35 (pago de salarios)

#### next_day_35(date_str: str) -> str
Retorna fecha del próximo día 35

#### days_between(date1: str, date2: str) -> int
Calcula días entre dos fechas

## Clase EventQueue

### Métodos Estáticos

#### add_event(events: List[Dict], event_type: str, date: str, data: Dict) -> List[Dict]
Añade evento a cola y ordena por fecha + ID

#### get_next_event(events: List[Dict]) -> Optional[Dict]
Obtiene próximo evento (primero en cola)

#### remove_event(events: List[Dict], event: Dict) -> List[Dict]
Elimina evento específico de cola

#### get_events_by_type(events: List[Dict], event_type: str) -> List[Dict]
Filtra eventos por tipo

## Funciones de Utilidad

### calculate_hire_time(dice_formula: str, experience_level: str, dice_roller) -> int
Calcula tiempo de búsqueda de contratación.

**Modificadores**:
- Novato: ceil(base/2)
- Estándar: base
- Veterano: base * 2

### calculate_hire_salary(base_salary: int, experience_level: str) -> int
Calcula salario según experiencia.

**Modificadores**:
- Novato: ceil(base/2)
- Estándar: base
- Veterano: base * 2

## Dependencias

- **math**: Para cálculos de ceil
- **typing**: Type hints

## Notas de Implementación

- **Calendario Personalizado**: 35 días/mes, 12 meses/año
- **Formato Fechas**: "dd-mm-yy" (día-mes-año)
- **Event Queue**: Ordenada por fecha, luego por ID
- **Overflow Handling**: Maneja correctamente cambios de mes/año

## Mejores Prácticas

- Usar métodos estáticos para operaciones puras
- Mantener cola de eventos ordenada
- Validar formato de fechas
- Usar compare_dates para lógica condicional