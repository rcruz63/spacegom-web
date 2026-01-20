# event_logger.py - Sistema de Logging de Eventos

## Overview

Módulo de logging centralizado para eventos del juego. Almacena eventos en el estado del juego y los muestra en la página de logs.

**Ubicación**: `app/event_logger.py`
**Líneas**: 173
**Dependencias**: `game_state`, `datetime`

## Clase EventLogger

### Inicialización
```python
logger = EventLogger(game_id)
```

### Método log(message: str, event_type: str = "info")
Registra evento en el log del juego.

**Tipos de evento**: "info", "success", "warning", "error"

### Método get_logs(limit: int = None, event_type: str = None)
Recupera logs del juego con filtros opcionales.

### Método clear_logs()
Limpia todos los logs (usar con precaución).

### Método Estático _log_to_game(game: GameState, message: str, event_type: str = "info")
Loggea a una instancia existente de GameState (evita crear nueva instancia).

## Funciones Helper de Formato

### format_hire_start(position: str, experience: str, days: int)
Formatea mensaje de inicio de búsqueda de contratación.

### format_hire_success(position: str, name: str, salary: int)
Formatea mensaje de contratación exitosa.

### format_hire_failure(position: str, experience: str)
Formatea mensaje de fallo en contratación.

### format_salary_payment(total: int, balance: int)
Formatea mensaje de pago de salarios.

### format_fire(position: str, name: str)
Formatea mensaje de despido.

### format_mission_start(mission_type: str, objective: str)
Formatea mensaje de inicio de misión.

### format_mission_complete(mission_type: str, objective: str, result: str)
Formatea mensaje de completación de misión.

## Estructura de Eventos

Cada evento en el log incluye:
- `game_date`: Fecha del juego (DD-MM-YYYY)
- `timestamp`: Timestamp real (ISO format)
- `message`: Mensaje descriptivo
- `type`: Tipo de evento

## Almacenamiento

Los logs se almacenan en `game.state["event_logs"]` como array de diccionarios.

## Dependencias

- **GameState**: Para persistencia de logs
- **datetime**: Para timestamps

## Notas de Implementación

- **Fechas Duales**: Registra tanto fecha del juego como timestamp real
- **Persistencia**: Logs se guardan automáticamente con game.save()
- **Filtrado**: Soporte para filtrar por tipo y límite
- **Helpers**: Funciones estáticas para mensajes consistentes

## Mejores Prácticas

- Usar tipos de evento apropiados
- Mantener mensajes descriptivos pero concisos
- Usar helpers de formato para consistencia
- Limpiar logs solo cuando necesario
- Evitar logs excesivos que puedan afectar performance