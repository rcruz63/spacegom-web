# models.py - Modelos de Datos Adicionales

## Overview

Archivo para modelos de datos adicionales usando SQLModel. Actualmente contiene modelos básicos que pueden extender la funcionalidad del sistema.

**Ubicación**: `app/models.py`
**Líneas**: ~10
**Dependencias**: `sqlmodel`

## Modelo EstadoPartida

Modelo básico para estado de partida usando SQLModel.

### Campos
- `id`: ID autoincremental, clave primaria

## Notas de Implementación

- **SQLModel**: Usa SQLModel en lugar de SQLAlchemy puro
- **Extensible**: Diseñado para agregar más modelos según necesidades
- **Básico**: Actualmente solo contiene estructura mínima

## Mejores Prácticas

- Usar SQLModel para nuevos modelos
- Mantener consistencia con modelos existentes en database.py
- Documentar campos y relaciones
- Considerar migración si se expande significativamente