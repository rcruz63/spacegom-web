# event_handlers.py - Sistema de Manejo de Eventos

## Overview

Sistema modular de handlers para eventos del juego. Cada tipo de evento tiene su propio handler que procesa lógica específica, actualiza estado y decide si remover el evento de la cola.

**Ubicación**: `app/event_handlers.py`
**Líneas**: 366
**Dependencias**: `game_state`, `database`, `time_manager`, `event_logger`, `personnel_manager`

## Clase EventHandlerResult

Resultado estandarizado de un event handler.

### Atributos
- `success`: Si el handler se ejecutó correctamente
- `remove_from_queue`: Si el evento debe borrarse de la cola
- `requires_user_input`: Si requiere interacción del usuario
- `event_data`: Datos adicionales del resultado

### Método `to_dict()`
Retorna representación diccionario.

## Handlers Implementados

### handle_salary_payment
Procesa pago mensual de salarios (día 35).

**Acciones**:
1. Calcula total de salarios de personal activo
2. Descuenta de tesorería
3. Registra transacción
4. Crea siguiente evento de pago
5. Logging

### handle_task_completion
Completa búsqueda de contratación de personal.

**Acciones**:
1. Calcula modificadores (experiencia, moral, reputación)
2. Tira dados para determinar éxito
3. Si éxito: crea nuevo empleado
4. Actualiza stats del Director
5. Inicia siguiente tarea en cola
6. Logging detallado

### handle_mission_deadline
Maneja fecha límite de misión.

**Acciones**:
1. Obtiene datos de la misión
2. Retorna datos para modal de usuario
3. NO borra evento (espera resolución manual)

## Registro de Handlers

### EVENT_HANDLERS
Diccionario que mapea tipos de eventos a funciones handler.

### get_event_handler(event_type: str)
Retorna el handler apropiado para un tipo de evento.

## Patrón de Diseño

- **Strategy Pattern**: Cada evento tiene su propia estrategia de procesamiento
- **Command Pattern**: Handlers encapsulan lógica compleja
- **Registry Pattern**: Registro centralizado de handlers

## Dependencias

- **GameState**: Para actualizar estado del juego
- **Database**: Para queries de personal, misiones, tareas
- **TimeManager**: Para cálculos de fechas y eventos
- **EventLogger**: Para logging de eventos
- **PersonnelManager**: Para actualizar stats de empleados

## Notas de Implementación

- **Transaccional**: Usa rollback si hay errores
- **Modular**: Fácil agregar nuevos tipos de eventos
- **User Input**: Algunos handlers requieren interacción del usuario
- **Queue Management**: Control preciso de cuándo remover eventos

## Mejores Prácticas

- Mantener handlers idempotentes
- Validar datos de entrada
- Usar logging consistente
- Documentar acciones de cada handler
- Probar handlers individualmente