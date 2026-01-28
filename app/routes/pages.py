"""
Routes para páginas HTML renderizadas con Jinja2.

Este módulo contiene los endpoints que devuelven páginas HTML completas
para la interfaz web de Spacegom.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory="app/templates")
templates.env.globals.update(chr=chr)


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    """Renderiza la página principal (`index.html`)."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Renderiza el panel de control (dashboard)."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request) -> HTMLResponse:
    """Renderiza la página de configuración inicial (setup)."""
    return templates.TemplateResponse("setup.html", {"request": request})


@router.get("/personnel", response_class=HTMLResponse)
async def personnel_page(request: Request) -> HTMLResponse:
    """Renderiza la página de gestión de personal."""
    return templates.TemplateResponse("personnel.html", {"request": request})


@router.get("/treasury", response_class=HTMLResponse)
async def treasury_page(request: Request) -> HTMLResponse:
    """Renderiza la página de tesorería y finanzas."""
    return templates.TemplateResponse("treasury.html", {"request": request})


@router.get("/missions", response_class=HTMLResponse)
async def missions_page(request: Request) -> HTMLResponse:
    """Renderiza la página de gestión de misiones."""
    return templates.TemplateResponse("missions.html", {"request": request})


@router.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request) -> HTMLResponse:
    """Renderiza la página de registros de eventos (logs)."""
    return templates.TemplateResponse("logs.html", {"request": request})


@router.get("/trade", response_class=HTMLResponse)
async def trade_page(request: Request) -> HTMLResponse:
    """Renderiza la página de comercio/mercado."""
    return templates.TemplateResponse("trade.html", {"request": request})
