## Stack tecnologico (versiones exactas detectadas)
- Python 3.12
- FastAPI 0.128.0
- Uvicorn 0.40.0
- SQLAlchemy 2.0.45
- SQLModel 0.0.31
- Jinja2 3.1.6
- boto3 1.42.30
- botocore 1.42.30
- pandas 2.3.3
- numpy 2.3.5
- openpyxl 3.1.5
- python-multipart 0.0.21
- flake8 7.3.0
- mypy 1.19.1
- pylint 4.0.4
- HTMX 1.9.10
- Docker base: ghcr.io/astral-sh/uv:python3.12-bookworm-slim

## Convenciones de codigo
- Python: funciones y variables en snake_case; clases en PascalCase.
- JS: funciones y variables en camelCase; clases en PascalCase.
- Plantillas HTML: Jinja2 con `{% extends "base.html" %}` y `{% block content %}`.
- Estructura: `app/` (backend), `app/templates/` (HTML), `app/static/js/` (JS), `files/` (CSV/PDF), `docs/` (documentacion).
- Lenguaje: comentarios, docstrings, mensajes, logs, interfaz web y commits en espanol de Espana.
- Commits: seguir Conventional Commits (v1.0.0-beta.2).

## Arquitectura (comunicacion front/back)
- FastAPI sirve HTML con Jinja2 y expone endpoints JSON bajo `/api/...`.
- Frontend usa `fetch` (JSON y FormData) contra `/api/...`.
- Hay endpoints de fragmentos HTML (HTMX) para casos legados (dados).
- Static assets se sirven desde `/static` y se montan en FastAPI.

## Reglas de Oro
- Nunca eliminar codigo funcional sin confirmacion explicita.
- Priorizar reutilizacion de funciones existentes.
- Mantener la separacion Frontend/Backend.
- Escribir docstrings en cualquier funcion nueva.
