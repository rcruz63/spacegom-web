"""
Script de ejecución principal para el servidor FastAPI.

Proporciona una función simple para iniciar el servidor FastAPI con
configuración de desarrollo (reload automático en cambios de código).

Dependencias:
    - uvicorn: Servidor ASGI para FastAPI
"""

import uvicorn


def start() -> None:
    """
    Inicia el servidor FastAPI con configuración de desarrollo.
    
    Configuración:
        - Host: 127.0.0.1 (localhost)
        - Puerto: 8000
        - Reload: True (reinicio automático en cambios de código)
    
    Uso:
        Desde línea de comandos:
        ```bash
        python -m app.run
        ```
        
        O desde pyproject.toml:
        ```bash
        uv run dev
        ```
    """
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
