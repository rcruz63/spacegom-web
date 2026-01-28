"""Módulo principal FastAPI.

Este módulo es el punto de entrada API de la aplicación Spacegom.
Inicializa la aplicación FastAPI y monta todos los routers organizados por dominio.

Resumen de responsabilidades:
- Carga de variables de entorno desde .env (load_dotenv) para AWS y DynamoDB
- Inicialización de FastAPI
- Configuración de archivos estáticos
- Montaje de routers desde app/routes/
- Evento de startup para inicializar la base de datos

Los endpoints están organizados en los siguientes módulos:
- routes/pages.py: Páginas HTML (index, dashboard, setup, etc.)
- routes/games.py: Gestión de juegos, setup, tiempo, exploración
- routes/dice_routes.py: Sistema de dados
- routes/planets.py: Planetas y sugerencias de nombres
- routes/personnel_routes.py: Personal y sistema de contratación
- routes/missions.py: Gestión de misiones
- routes/commerce.py: Tesorería, comercio y transporte de pasajeros
"""
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env lo antes posible (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, etc.)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import all_routers

app = FastAPI(
    title="Spacegom API",
    description="API para el juego de gestión espacial Spacegom",
    version="1.0.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include all routers
for router in all_routers:
    app.include_router(router)


@app.on_event("startup")
async def startup_event() -> None:
    """Inicializa recursos al arrancar la aplicación.

    Llama a `init_db()` para asegurar que la base de datos y las tablas
    requeridas existen o se migran cuando arranca la aplicación FastAPI.
    """
    init_db()
