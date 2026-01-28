"""
Routes para páginas HTML renderizadas con Jinja2.

Este módulo contiene los endpoints que devuelven páginas HTML completas
para la interfaz web de Spacegom. Todas las rutas renderizan templates
Jinja2 desde app/templates/.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])

# Configuración de templates Jinja2
templates = Jinja2Templates(directory="app/templates")
# Añadir función chr() como global para uso en templates
templates.env.globals.update(chr=chr)


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    """
    Renderiza la página principal (landing page).
    
    Muestra lista de partidas guardadas, estadísticas y opciones para iniciar
    nueva partida o continuar la última.
    
    Args:
        request: Request de FastAPI (para renderizado de template)
    
    Returns:
        HTMLResponse con el template index.html renderizado
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """
    Renderiza el panel de control principal (dashboard).
    
    Muestra estado general del juego, información del planeta actual, HUD
    de la nave y widgets de acciones disponibles.
    
    Args:
        request: Request de FastAPI (para renderizado de template)
    
    Returns:
        HTMLResponse con el template dashboard.html renderizado
    
    Note:
        Requiere game_id en query parameters para mostrar información del juego.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request) -> HTMLResponse:
    """
    Renderiza la página de configuración inicial de partida (setup wizard).
    
    Guía al jugador a través del proceso completo de setup paso a paso:
    identificación, determinación de área, densidad, posición, planeta inicial
    y dificultad.
    
    Args:
        request: Request de FastAPI (para renderizado de template)
    
    Returns:
        HTMLResponse con el template setup.html renderizado
    """
    return templates.TemplateResponse("setup.html", {"request": request})


@router.get("/personnel", response_class=HTMLResponse)
async def personnel_page(request: Request) -> HTMLResponse:
    """
    Renderiza la página de gestión de personal.
    
    Muestra personal activo, permite iniciar búsquedas de contratación y gestionar
    la cola de tareas del Director Gerente.
    
    Args:
        request: Request de FastAPI (para renderizado de template)
    
    Returns:
        HTMLResponse con el template personnel.html renderizado
    
    Note:
        Requiere game_id en query parameters.
    """
    return templates.TemplateResponse("personnel.html", {"request": request})


@router.get("/treasury", response_class=HTMLResponse)
async def treasury_page(request: Request) -> HTMLResponse:
    """
    Renderiza la página de tesorería y finanzas.
    
    Muestra saldo actual, gastos mensuales, permite registrar transacciones
    manuales y ver historial completo de transacciones.
    
    Args:
        request: Request de FastAPI (para renderizado de template)
    
    Returns:
        HTMLResponse con el template treasury.html renderizado
    
    Note:
        Requiere game_id en query parameters.
    """
    return templates.TemplateResponse("treasury.html", {"request": request})


@router.get("/missions", response_class=HTMLResponse)
async def missions_page(request: Request) -> HTMLResponse:
    """
    Renderiza la página de gestión de misiones.
    
    Permite crear objetivos de campaña y misiones especiales, ver misiones
    activas/completadas/fallidas y gestionar su estado.
    
    Args:
        request: Request de FastAPI (para renderizado de template)
    
    Returns:
        HTMLResponse con el template missions.html renderizado
    
    Note:
        Requiere game_id en query parameters.
    """
    return templates.TemplateResponse("missions.html", {"request": request})


@router.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request) -> HTMLResponse:
    """
    Renderiza la página de registros de eventos (logs).
    
    Muestra el historial completo de eventos del juego con filtrado por tipo
    y orden cronológico.
    
    Args:
        request: Request de FastAPI (para renderizado de template)
    
    Returns:
        HTMLResponse con el template logs.html renderizado
    
    Note:
        Requiere game_id en query parameters.
    """
    return templates.TemplateResponse("logs.html", {"request": request})


@router.get("/trade", response_class=HTMLResponse)
async def trade_page(request: Request) -> HTMLResponse:
    """
    Renderiza la página de comercio/mercado.
    
    Muestra productos disponibles para compra/venta, permite negociar precios
    con tiradas de dados y gestionar cesta de compra y órdenes comerciales.
    
    Args:
        request: Request de FastAPI (para renderizado de template)
    
    Returns:
        HTMLResponse con el template trade.html renderizado
    
    Note:
        Requiere game_id en query parameters.
    """
    return templates.TemplateResponse("trade.html", {"request": request})
