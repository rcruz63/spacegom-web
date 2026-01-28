"""
Routes package for Spacegom API.

Este paquete contiene todos los routers de FastAPI organizados por dominio.
"""
from fastapi import APIRouter

from app.routes.pages import router as pages_router
from app.routes.games import router as games_router
from app.routes.dice_routes import router as dice_router
from app.routes.planets import router as planets_router
from app.routes.personnel_routes import router as personnel_router
from app.routes.missions import router as missions_router
from app.routes.commerce import router as commerce_router

# Lista de todos los routers para facilitar el montaje en main.py
all_routers = [
    pages_router,
    games_router,
    dice_router,
    planets_router,
    personnel_router,
    missions_router,
    commerce_router,
]

__all__ = [
    "pages_router",
    "games_router", 
    "dice_router",
    "planets_router",
    "personnel_router",
    "missions_router",
    "commerce_router",
    "all_routers",
]
