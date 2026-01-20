# run.py - Script de Ejecución Principal

## Overview

Script simple para iniciar el servidor FastAPI con configuración de desarrollo.

**Ubicación**: `app/run.py`
**Líneas**: ~10
**Dependencias**: `uvicorn`

## Función start()

Inicia el servidor FastAPI con configuración de desarrollo.

**Configuración**:
- Host: 127.0.0.1
- Puerto: 8000
- Reload: True (reinicio automático en cambios)

## Uso

```bash
python -m app.run
```

O desde pyproject.toml:
```bash
uv run dev
```

## Notas de Implementación

- **Desarrollo**: Configurado para desarrollo local
- **Reload**: Detecta cambios automáticamente
- **Simple**: Punto de entrada minimalista

## Mejores Prácticas

- Usar solo para desarrollo local
- Para producción, usar configuración específica
- Considerar variables de entorno para host/puerto