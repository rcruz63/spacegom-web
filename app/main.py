from fastapi import FastAPI, Form, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Any, Dict
"""Módulo principal FastAPI.

Este módulo es el punto de entrada API de la aplicación Spacegom. Expone
rutas que renderizan páginas HTML y un API REST JSON consumido por el
frontend. Fragmentos relevantes de la documentación del proyecto han sido
embebidos como docstrings y comentarios dentro del código para mantener la
información cerca de la implementación.

Resumen de responsabilidades:
- Páginas web: index, dashboard, setup, personnel, treasury, missions, logs, trade.
- Gestión de juegos: creación/listado, lectura/actualización de estado, logs y setup.
- Sistema de dados: `DiceRoller` con endpoint HTMX legado y API JSON.
- Planetas: obtención por código 3d6, validación para planeta inicial, notas/bootstrap.
- Personal y contratación: modelos `Personnel` y `EmployeeTask`.
- Tiempo y eventos: `GameCalendar` y `EventQueue` para eventos programados.
- Comercio y pasajeros: gestores específicos encapsulan reglas de negocio.

Todos los endpoints públicos incluyen anotaciones de tipo y docstrings
concisos en español para facilitar su lectura por desarrolladores y linters.
"""
import random
import json
import math

from app.database import get_db, Planet, Personnel, INITIAL_PERSONNEL, Mission, EmployeeTask, POSITIONS_CATALOG, TECH_LEVEL_REQUIREMENTS, init_db
from app.game_state import GameState
from app.dice import DiceRoller
from app.time_manager import GameCalendar, EventQueue, calculate_hire_time, calculate_hire_salary
from app.name_suggestions import get_random_company_name, get_random_ship_name

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
templates.env.globals.update(chr=chr)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize database on startup
@app.on_event("startup")
async def startup_event() -> None:
    """Inicializa recursos al arrancar la aplicación.

    Llama a `init_db()` para asegurar que la base de datos y las tablas
    requeridas existen o se migran cuando arranca la aplicación FastAPI.
    """
    init_db()


# ===== WEB PAGES =====

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    """Renderiza la página principal (`index.html`)."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Renderiza el panel de control (dashboard)."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request) -> HTMLResponse:
    """Renderiza la página de configuración inicial (setup)."""
    return templates.TemplateResponse("setup.html", {"request": request})

@app.get("/personnel", response_class=HTMLResponse)
async def personnel_page(request: Request) -> HTMLResponse:
    """Renderiza la página de gestión de personal."""
    return templates.TemplateResponse("personnel.html", {"request": request})

@app.get("/treasury", response_class=HTMLResponse)
async def treasury_page(request: Request) -> HTMLResponse:
    """Renderiza la página de tesorería y finanzas."""
    return templates.TemplateResponse("treasury.html", {"request": request})

@app.get("/missions", response_class=HTMLResponse)
async def missions_page(request: Request) -> HTMLResponse:
    """Renderiza la página de gestión de misiones."""
    return templates.TemplateResponse("missions.html", {"request": request})

@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request) -> HTMLResponse:
    """Renderiza la página de registros de eventos (logs)."""
    return templates.TemplateResponse("logs.html", {"request": request})

@app.get("/trade", response_class=HTMLResponse)
async def trade_page(request: Request) -> HTMLResponse:
    """Renderiza la página de comercio/mercado."""
    return templates.TemplateResponse("trade.html", {"request": request})


# ===== GAME MANAGEMENT API =====

@app.get("/api/games")
async def list_games() -> Dict[str, Any]:
    """Listar todos los juegos disponibles.

    Devuelve un diccionario JSON con la clave `games` que contiene la
    información de los juegos existentes.
    """
    games = GameState.list_games()
    return {"games": games}

@app.post("/api/games/new")
async def create_game(game_name: Optional[str] = Form(None)) -> Dict[str, Any]:
    """Crear un nuevo juego.

    Crea y persiste un nuevo `GameState`. Devuelve `game_id` y el estado
    inicial del juego.
    """
    game = GameState.create_new_game(game_name)
    game.save()
    return {"game_id": game.game_id, "state": game.state}

@app.get("/api/games/{game_id}")
async def get_game_state(game_id: str) -> Dict[str, Any]:
    """Obtener el estado actual del juego.

    Devuelve el estado persistido y las estadísticas de la nave derivadas
    del `ship_model` guardado en el estado.
    """
    from app.ship_data import get_ship_stats
    game = GameState(game_id)
    ship_stats = get_ship_stats(game.state.get("ship_model", "Basic Starfall"))
    return {
        "state": game.state,
        "ship_stats": ship_stats
    }

@app.post("/api/games/{game_id}/update")
async def update_game_state(
    game_id: str,
    fuel: Optional[int] = Form(None),
    storage: Optional[int] = Form(None),
    month: Optional[int] = Form(None),
    reputation: Optional[int] = Form(None),
    damage_light: Optional[bool] = Form(None),
    damage_moderate: Optional[bool] = Form(None),
    damage_severe: Optional[bool] = Form(None)
) -> Dict[str, Any]:
    """Actualizar campos del estado del juego.

    Realiza validaciones básicas y límites (por ejemplo, combustible entre
    0 y `fuel_max`) y actualiza indicadores booleanos de daños.
    Devuelve el estado actualizado.
    """
    game = GameState(game_id)
    
    if fuel is not None:
        game.state["fuel"] = max(0, min(game.state["fuel_max"], fuel))
    if storage is not None:
        game.state["storage"] = max(0, min(game.state["storage_max"], storage))
    if month is not None:
        game.state["month"] = max(1, min(12, month))
    if reputation is not None:
        game.state["reputation"] = max(-5, min(5, reputation))
    
    if damage_light is not None:
        game.state["damages"]["light"] = damage_light
    if damage_moderate is not None:
        game.state["damages"]["moderate"] = damage_moderate
    if damage_severe is not None:
        game.state["damages"]["severe"] = damage_severe
    
    game.save()
    return {"state": game.state}


@app.get("/api/games/{game_id}/logs")
async def get_logs(
    game_id: str,
    limit: Optional[int] = None,
    event_type: Optional[str] = None
) -> Dict[str, Any]:
    """Obtener registros de eventos del juego.

    Soporta filtros `limit` y `event_type`. Devuelve la lista `logs` y el
    recuento `count`.
    """
    from app.event_logger import EventLogger
    
    logger = EventLogger(game_id)
    logs = logger.get_logs(limit=limit, event_type=event_type)
    
    return {
        "logs": logs,
        "count": len(logs)
    }



@app.post("/api/games/{game_id}/update-location")
async def update_ship_location(
    game_id: str,
    location: str = Form(...)
 ) -> Dict[str, Any]:
    """Actualizar la ubicación de la nave en el planeta (por ejemplo, "Mundo", "Espaciopuerto")."""
    game = GameState(game_id)
    game.state["ship_location_on_planet"] = location
    game.save()
    return {"status": "success", "location": location}

@app.post("/api/games/{game_id}/company-setup")
async def company_setup(
    game_id: str,
    company_name: str = Form(...),
    ship_name: str = Form(...),
    ship_model: str = Form("Basic Starfall")
 ) -> Dict[str, Any]:
    """Guardar los datos de la compañía y la nave del jugador.

    Inicializa estadísticas de la nave en función del `ship_model`.
    """
    from app.ship_data import get_ship_stats
    
    game = GameState(game_id)
    game.state["company_name"] = company_name
    game.state["ship_name"] = ship_name
    game.state["ship_model"] = ship_model
    
    # Initialize ship stats from model
    stats = get_ship_stats(ship_model)
    game.state["fuel_max"] = stats["jump"] * 30 # Simple logic: 30 fuel per jump capacity? 
    # Actually user says storage is 40 UCN for Basic Starfall
    game.state["storage_max"] = stats["storage"]
    
    game.save()
    return {"status": "success", "state": game.state}


@app.post("/api/games/{game_id}/setup")
async def initial_company_setup(
    game_id: str,
    area_manual: Optional[str] = Form(None),  # e.g., "4,5" for manual 2d6
    density_manual: Optional[str] = Form(None)  # e.g., "6,3" for manual 2d6
 ) -> Dict[str, Any]:
    """Configuración inicial de la compañía.

    Paso 1: tirar 2d6 para área espacial (2-12).
    Paso 2: tirar 2d6 para densidad de mundos y determinar nivel:
        - 2-4: Baja
        - 5-9: Media
        - 10-12: Alta

    Parámetros opcionales `area_manual` y `density_manual` permiten
    proporcionar resultados manuales separados por comas.
    """
    game = GameState(game_id)
    
    # Step 1: Determine area (2d6)
    area_is_manual = False
    area_results = []
    
    if area_manual and area_manual.strip():
        try:
            area_results = [int(x.strip()) for x in area_manual.split(",")]
            if len(area_results) != 2:
                raise ValueError("Need exactly 2 dice for area")
            if any(r < 1 or r > 6 for r in area_results):
                raise ValueError("Dice results must be between 1 and 6")
            area_is_manual = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid area_manual: {e}")
    else:
        area_results = DiceRoller.roll_dice(num_dice=2)
    
    area = sum(area_results)
    game.record_dice_roll(2, area_results, area_is_manual, "initial_area")
    
    # Step 2: Determine world density (2d6)
    density_is_manual = False
    density_results = []
    
    if density_manual and density_manual.strip():
        try:
            density_results = [int(x.strip()) for x in density_manual.split(",")]
            if len(density_results) != 2:
                raise ValueError("Need exactly 2 dice for density")
            if any(r < 1 or r > 6 for r in density_results):
                raise ValueError("Dice results must be between 1 and 6")
            density_is_manual = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid density_manual: {e}")
    else:
        density_results = DiceRoller.roll_dice(num_dice=2)
    
    density_total = sum(density_results)
    world_density = DiceRoller.world_density_from_roll(density_total)
    game.record_dice_roll(2, density_results, density_is_manual, "world_density")
    
    # Update game state
    game.state["area"] = area
    game.state["current_area"] = area  # Start in the same area
    game.state["world_density"] = world_density
    game.state["setup_complete"] = True
    
    game.add_event(
        "initial_setup",
        f"Empresa establecida en Área {area} con densidad de mundos {world_density}",
        {
            "area": area,
            "world_density": world_density,
            "area_roll": area_results,
            "density_roll": density_results
        }
    )
    
    game.save()
    
    return {
        "area": {
            "value": area,
            "dice": area_results,
            "is_manual": area_is_manual
        },
        "world_density": {
            "level": world_density,
            "total": density_total,
            "dice": density_results,
            "is_manual": density_is_manual
        },
        "setup_complete": True,
        "state": game.state
    }


@app.post("/api/games/{game_id}/setup-position")
async def initial_position_setup(
    game_id: str,
    row_manual: Optional[int] = Form(None),
    col_manual: Optional[int] = Form(None)
 ) -> Dict[str, Any]:
    """Configuración inicial de la posición de la nave.

    Se tiran 1d6 para fila y 1d6 para columna (valores 1-6).
    """
    game = GameState(game_id)
    
    # Row setup
    row_is_manual = False
    if row_manual is not None:
        if 1 <= row_manual <= 6:
            row_results = [row_manual]
            row_is_manual = True
        else:
            raise HTTPException(status_code=400, detail="Row dice must be between 1 and 6")
    else:
        row_results = DiceRoller.roll_dice(num_dice=1)
    
    row_val = row_results[0]
    game.record_dice_roll(1, row_results, row_is_manual, "initial_row")
    
    # Col setup
    col_is_manual = False
    if col_manual is not None:
        if 1 <= col_manual <= 6:
            col_results = [col_manual]
            col_is_manual = True
        else:
            raise HTTPException(status_code=400, detail="Col dice must be between 1 and 6")
    else:
        col_results = DiceRoller.roll_dice(num_dice=1)
        
    col_val = col_results[0]
    game.record_dice_roll(1, col_results, col_is_manual, "initial_col")
    
    # Update game state (storing 1-6 in ship_row/ship_col for display)
    game.state["ship_row"] = row_val
    game.state["ship_col"] = col_val
    game.state["ship_pos_complete"] = True
    
    # First exploration of current quadrant (internal storage uses 0-based)
    game.explore_quadrant(row_val - 1, col_val - 1)
    
    game.add_event(
        "initial_position",
        f"Posición inicial establecida en Cuadrante {chr(64+col_val)}{row_val}",
        {"row": row_val, "col": col_val}
    )
    
    game.save()
    
    return {
        "row": row_val,
        "col": col_val,
        "col_letter": chr(64+col_val),
        "ship_pos_complete": True,
        "state": game.state
    }


@app.post("/api/planets/{code}/update-bootstrap")
async def update_planet_bootstrap(
    code: int,
    tech_level: str = Form(...),
    population_over_1000: bool = Form(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Actualizar datos faltantes del planeta para el proceso de bootstrap.

    Se usa en el flujo de bootstrap cuando faltan datos técnicos del
    planeta y el jugador los proporciona manualmente (`tech_level` y
    `population_over_1000`).
    """
    planet = db.query(Planet).filter(Planet.code == code).first()
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {code} not found")
    
    planet.tech_level = tech_level
    planet.population_over_1000 = population_over_1000
    db.commit()
    
    return {"status": "success", "planet": {"code": code, "tech_level": tech_level, "population_over_1000": population_over_1000}}


# ===== DICE ROLLING API =====

@app.post("/api/roll-dice", response_class=HTMLResponse)
async def roll_dice(request: Request, num_dices: int = Form(1), manual_result: str | None = Form(None)) -> HTMLResponse:
    """Tirada de dados (endpoint legado para HTMX).

    Devuelve un fragmento HTML (`components/dice_result.html`) usado por la
    interfaz HTMX. Para clientes programáticos, se recomiendan los
    endpoints JSON.
    """
    is_manual = False
    result_val = 0
    details = ""

    if manual_result and manual_result.strip():
        try:
            result_val = int(manual_result)
            is_manual = True
        except ValueError:
            result_val = 0
            details = "Error: Invalid manual input"
    else:
        rolls = DiceRoller.roll_dice(num_dices)
        result_val = sum(rolls)
        details = f"Rolls: {rolls}"

    return templates.TemplateResponse("components/dice_result.html", {
        "request": request, 
        "result": result_val, 
        "details": details,
        "is_manual": is_manual
    })


@app.post("/api/dice/roll")
async def roll_dice_universal(request: Request) -> Dict[str, Any]:
    """Endpoint universal de tiradas de dados (JSON).

    Espera un JSON con `num_dice`, `dice_sides` y opcionalmente
    `manual_values`. Devuelve los resultados de los dados, la suma y el
    modo (`manual` o `automatic`).
    """
    try:
        data = await request.json()
        num_dice = data.get('num_dice', 1)
        dice_sides = data.get('dice_sides', 6)
        manual_values = data.get('manual_values')
        
        if manual_values:
            # Validate manual values
            if len(manual_values) != num_dice:
                raise HTTPException(400, f"Expected {num_dice} dice values, got {len(manual_values)}")
            for val in manual_values:
                if val < 1 or val > dice_sides:
                    raise HTTPException(400, f"All dice values must be between 1 and {dice_sides}")
            results = manual_values
            mode = "manual"
        else:
            # Automatic roll
            results = DiceRoller.roll_dice(num_dice, dice_sides)
            mode = "automatic"
        
        return {
            "dice": results,
            "sum": sum(results),
            "mode": mode,
            "num_dice": num_dice,
            "dice_sides": dice_sides
        }
    except HTTPException:
        raise
    except Exception as e:
        # logger.error(f"Error in universal dice roll: {e}")
        raise HTTPException(500, str(e))


@app.post("/api/games/{game_id}/roll")
async def roll_dice_json(
    game_id: str,
    num_dice: int = Form(1),
    manual_results: Optional[str] = Form(None),
    purpose: str = Form("")
 ) -> Dict[str, Any]:
    """Tirar dados y registrar la tirada en el historial del juego.

    Los parámetros coinciden con el formulario de la interfaz. Devuelve
    los resultados, el total, si fue manual y una representación
    formateada. El campo `purpose` se usa para etiquetar la tirada.
    """
    game = GameState(game_id)
    
    is_manual = False
    results = []
    
    if manual_results and manual_results.strip():
        # Parse manual results
        try:
            results = [int(x.strip()) for x in manual_results.split(",")]
            if len(results) != num_dice:
                raise ValueError(f"Expected {num_dice} results, got {len(results)}")
            if any(r < 1 or r > 6 for r in results):
                raise ValueError("All results must be between 1 and 6")
            is_manual = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        # Automatic roll
        results = DiceRoller.roll_dice(num_dice)
    
    # Record in game history
    roll_data = game.record_dice_roll(num_dice, results, is_manual, purpose)
    
    return {
        "results": results,
        "total": sum(results),
        "is_manual": is_manual,
        "purpose": purpose,
        "formatted": DiceRoller.format_results(results)
    }

@app.post("/api/games/{game_id}/roll-planet-code")
async def roll_planet_code(
    game_id: str,
    manual_results: Optional[str] = Form(None),
    db: Session = Depends(get_db)
 ) -> Dict[str, Any]:
    """Tirar 3d6 para generar un código de planeta y devolver sus datos.

    Si el planeta no existe en la base de datos, se devuelve `planet: None`.
    """
    game = GameState(game_id)
    
    is_manual = False
    
    if manual_results and manual_results.strip():
        try:
            results = [int(x.strip()) for x in manual_results.split(",")]
            if len(results) != 3:
                raise ValueError("Need exactly 3 dice for planet code")
            if any(r < 1 or r > 6 for r in results):
                raise ValueError("All results must be between 1 and 6")
            is_manual = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        code = DiceRoller.results_to_code(results)
    else:
        code, results = DiceRoller.roll_for_planet_code()
    
    # Record roll
    game.record_dice_roll(3, results, is_manual, "planet_code")
    
    # Fetch planet from database
    planet = db.query(Planet).filter(Planet.code == code).first()
    
    if not planet:
        return {
            "code": code,
            "dice": results,
            "planet": None,
            "error": f"Planet with code {code} not found in database"
        }
    
    return {
        "code": code,
        "dice": results,
        "planet": format_planet_data(planet),
        "is_valid_start": is_valid_starting_planet(planet)
    }


def format_planet_data(planet: Planet) -> dict:
    """Formatea los datos de un `Planet` para las respuestas de la API.

    Args:
        planet: Instancia de `Planet` obtenida de la base de datos.

    Returns:
        dict: Diccionario con la información del planeta en formato legible.
    """
    from app.utils import decode_life_support, decode_tech_level, parse_spaceport
    
    # Parse spaceport into components
    spaceport_str = f"{planet.spaceport_quality}-{planet.fuel_density}-{planet.docking_price}"
    spaceport_decoded = parse_spaceport(spaceport_str)
    
    return {
        "code": planet.code,
        "name": planet.name,
        "life_support": {
            "type": planet.life_support,
            "description": decode_life_support(planet.life_support),
            "local_contagion_risk": planet.local_contagion_risk,
            "days_to_hyperspace": planet.days_to_hyperspace,
            "legal_order_threshold": planet.legal_order_threshold
        },
        "spaceport": {
            "raw": spaceport_str,
            "quality_code": planet.spaceport_quality,
            "quality": spaceport_decoded["quality"],
            "fuel_code": planet.fuel_density,
            "fuel": spaceport_decoded["fuel"],
            "docking_price": planet.docking_price
        },
        "orbital_facilities": {
            "cartography_center": planet.orbital_cartography_center,
            "hackers": planet.orbital_hackers,
            "supply_depot": planet.orbital_supply_depot,
            "astro_academy": planet.orbital_astro_academy
        },
        "products": {
            "INDU": planet.product_indu,
            "BASI": planet.product_basi,
            "ALIM": planet.product_alim,
            "MADE": planet.product_made,
            "AGUA": planet.product_agua,
            "MICO": planet.product_mico,
            "MIRA": planet.product_mira,
            "MIPR": planet.product_mipr,
            "PAVA": planet.product_pava,
            "A": planet.product_a,
            "AE": planet.product_ae,
            "AEI": planet.product_aei,
            "COM": planet.product_com
        },
        "trade_info": {
            "self_sufficiency_level": planet.self_sufficiency_level,
            "ucn_per_order": planet.ucn_per_order,
            "max_passengers": planet.max_passengers,
            "mission_threshold": planet.mission_threshold
        },
        "bootstrap_data": {
            "tech_level": planet.tech_level,
            "tech_level_description": decode_tech_level(planet.tech_level) if planet.tech_level else "Desconocido",
            "population_over_1000": planet.population_over_1000,
            "convenio_spacegom": planet.convenio_spacegom
        },
        "notes": planet.notes
    }


def is_valid_starting_planet(planet: Planet) -> dict:
    """
    Check if planet is valid for starting position
    
    Requirements:
    - Population > 1000
    - Tech level not PR (Primitivo) or RUD (Rudimentario)
    - Life support not TA (Traje Avanzado) or TH (Traje Hiperavanzado)
    - Convenio Spacegom = True
    - At least one product available
    """
    checks = {
        "population": planet.population_over_1000 is True,
        "tech_level": planet.tech_level not in [None, "PR", "RUD"],
        "life_support": planet.life_support not in ["TA", "TH"],
        "convenio": planet.convenio_spacegom is True,
        "has_product": any([
            planet.product_indu, planet.product_basi, planet.product_alim,
            planet.product_made, planet.product_agua, planet.product_mico,
            planet.product_mira, planet.product_mipr, planet.product_pava,
            planet.product_a, planet.product_ae, planet.product_aei,
            planet.product_com
        ])
    }
    
    return {
        "is_valid": all(checks.values()),
        "checks": checks
    }


# ===== PLANET API =====

@app.get("/api/planets/{code}")
async def get_planet(code: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener un planeta por su código.

    Devuelve los datos formateados del planeta y la validación para
    determinar si es apto como planeta inicial.
    """
    planet = db.query(Planet).filter(Planet.code == code).first()
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {code} not found")
    
    return {
        "planet": format_planet_data(planet),
        "is_valid_start": is_valid_starting_planet(planet)
    }

@app.get("/api/planets")
async def search_planets(name: Optional[str] = None, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Buscar planetas por nombre.

    Devuelve una lista de coincidencias (límite 50).
    """
    query = db.query(Planet)
    
    if name:
        query = query.filter(Planet.name.ilike(f"%{name}%"))
    
    planets = query.limit(50).all()
    
    return {
        "planets": [
            {
                "code": p.code,
                "name": p.name,
                "spaceport": p.spaceport
            }
            for p in planets
        ]
    }


@app.post("/api/games/{game_id}/set-starting-planet")
async def set_starting_planet(game_id: str, code: int = Form(...)) -> Dict[str, Any]:
    """Establece el planeta inicial para la partida.

    Actualiza el `GameState` y marca el planeta como descubierto en el
    cuadrante actual si existe información de posición.
    """
    game = GameState(game_id)
    game.state["current_planet_code"] = code
    game.state["starting_planet_code"] = code
    
    # Set default ship location to Mundo (surface)
    if "ship_location_on_planet" not in game.state or not game.state["ship_location_on_planet"]:
        game.state["ship_location_on_planet"] = "Mundo"
    
    # Also record it in the current quadrant
    # ship_row and ship_col are 1-based (1-6), but internal storage is 0-based (0-5)
    row = game.state.get("ship_row")
    col = game.state.get("ship_col")
    if row and col:
        # Convert to 0-based for internal storage
        game.discover_planet(row - 1, col - 1, code)
        game.explore_quadrant(row - 1, col - 1)
        
    game.save()
    return {"status": "success", "code": code}



@app.get("/api/planets/next/{current_code}")
async def get_next_planet(current_code: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene el siguiente planeta en la secuencia 3d6 (búsqueda consecutiva)
    
    Este endpoint implementa la lógica del manual de juego:
    Si el planeta no es apto para inicio, se busca el siguiente código
    en orden (111 → 112 → 113...) hasta encontrar uno válido.
    
    Args:
        current_code: Código del planeta actual (111-666)
        
    Returns:
        JSON con información del siguiente planeta y validación de inicio
    """
    # Calcular el siguiente código en la secuencia
    next_code = DiceRoller.get_next_planet_code(current_code)
    planet = db.query(Planet).filter(Planet.code == next_code).first()
    
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {next_code} not found")
        
    return {
        "planet": format_planet_data(planet),
        "is_valid_start": is_valid_starting_planet(planet)
    }


@app.post("/api/planets/{code}/update-notes")
async def update_planet_notes(
    code: int,
    notes: str = Form(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Actualizar notas de un planeta
    
    Args:
        code: Código del planeta
        notes: Texto de las notas
        
    Returns:
        El planeta actualizado
    """
    planet = db.query(Planet).filter(Planet.code == code).first()
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {code} not found")
    
    planet.notes = notes
    db.commit()
    db.refresh(planet)
    
    return {
        "status": "success",
        "planet": format_planet_data(planet)
    }


# ===== NAME SUGGESTIONS API =====

@app.get("/api/suggestions/company-name")
async def suggest_company_name() -> Dict[str, Any]:
    """
    Retorna un nombre de compañía aleatorio desde el CSV
    
    Returns:
        JSON con el nombre sugerido
    """
    return {"name": get_random_company_name()}


@app.get("/api/suggestions/ship-name")
async def suggest_ship_name() -> Dict[str, Any]:
    """
    Retorna un nombre de nave aleatorio desde el CSV
    
    Returns:
        JSON con el nombre sugerido
    """
    return {"name": get_random_ship_name()}


# ===== EXPLORATION API =====

@app.post("/api/games/{game_id}/explore")
async def explore_quadrant(
    game_id: str,
    row: int = Form(...),
    col: int = Form(...)
) -> Dict[str, Any]:
    """Marcar un cuadrante como explorado.

    Actualiza el estado del juego para reflejar la exploración y devuelve
    la lista actualizada de cuadrantes explorados.
    """
    game = GameState(game_id)
    game.explore_quadrant(row, col)
    
    return {
        "explored": True,
        "quadrant": f"{row},{col}",
        "explored_quadrants": game.state["explored_quadrants"]
    }


@app.post("/api/games/{game_id}/navigate-area")
async def navigate_area(
    game_id: str,
    direction: str = Form(...)
) -> Dict[str, Any]:
    """Navegar a un área adyacente (anterior/siguiente).

    Args:
        game_id: Identificador de la partida.
        direction: "prev" o "next" indicando dirección.

    Returns:
        JSON con el nuevo número de área y el estado de la operación.
    """
    game = GameState(game_id)
    current_area = game.state.get("area", 2)
    
    if direction == "prev" and current_area > 2:
        game.state["area"] = current_area - 1
        game.save()
        return {"success": True, "new_area": current_area - 1}
    elif direction == "next" and current_area < 12:
        game.state["area"] = current_area + 1
        game.save()
        return {"success": True, "new_area": current_area + 1}
    else:
        return {"success": False, "new_area": current_area, "message": "Area limit reached"}


@app.get("/api/games/{game_id}/area/{area_number}/planets")
async def get_area_planets(
    game_id: str,
    area_number: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all discovered planets in a specific area
    
    Args:
        game_id: Game identifier
        area_number: Area number (2-12)
        
    Returns:
        JSON with list of planets discovered in the area with full data
    """
    game = GameState(game_id)
    
    # Filter discovered planets by area
    area_planets = []
    for code, info in game.state.get("discovered_planets", {}).items():
        if info["area"] == area_number:
            planet = db.query(Planet).filter(Planet.code == int(code)).first()
            if planet:
                planet_data = format_planet_data(planet)
                planet_data["quadrant"] = info["quadrant"]  # Add quadrant info
                area_planets.append(planet_data)
    
    # Get current ship position info
    current_planet_code = game.state.get("current_planet_code")
    ship_quadrant = f"{game.state.get('ship_row')},{game.state.get('ship_col')}"
    
    return {
        "planets": area_planets,
        "area": area_number,
        "count": len(area_planets),
        "current_planet_code": current_planet_code,
        "ship_quadrant": ship_quadrant
    }

# ===== PERSONNEL API =====

@app.get("/api/games/{game_id}/personnel")
async def get_personnel(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get all personnel for a game
    
    Returns:
        List of active personnel with total monthly salaries
    """
    personnel = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.is_active == True
    ).all()
    
    personnel_list = [{
        "id": p.id,
        "position": p.position,
        "name": p.name,
        "monthly_salary": p.monthly_salary,
        "experience": p.experience,
        "morale": p.morale,
        "hire_date": p.hire_date,
        "notes": p.notes
    } for p in personnel]
    
    total_monthly_salaries = sum(p.monthly_salary for p in personnel)
    
    return {
        "personnel": personnel_list,
        "total_monthly_salaries": total_monthly_salaries,
        "count": len(personnel)
    }


@app.post("/api/games/{game_id}/personnel")
async def hire_personnel(
    game_id: str,
    position: str = Form(...),
    name: str = Form(...),
    monthly_salary: int = Form(...),
    experience: str = Form(...),
    morale: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Contratar nuevo personal.

    Crea una fila `Personnel` y devuelve la información del empleado creado.
    """
    from datetime import date
    
    new_employee = Personnel(
        game_id=game_id,
        position=position,
        name=name,
        monthly_salary=monthly_salary,
        experience=experience,
        morale=morale,
        hire_date=date.today().isoformat(),
        is_active=True,
        notes=notes
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return {
        "status": "success",
        "employee": {
            "id": new_employee.id,
            "name": new_employee.name,
            "position": new_employee.position
        }
    }


@app.put("/api/games/{game_id}/personnel/{employee_id}")
async def update_personnel(
    game_id: str,
    employee_id: int,
    position: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    monthly_salary: Optional[int] = Form(None),
    experience: Optional[str] = Form(None),
    morale: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Actualizar información de personal y persistir los cambios."""
    employee = db.query(Personnel).filter(
        Personnel.id == employee_id,
        Personnel.game_id == game_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if position is not None:
        employee.position = position
    if name is not None:
        employee.name = name
    if monthly_salary is not None:
        employee.monthly_salary = monthly_salary
    if experience is not None:
        employee.experience = experience
    if morale is not None:
        employee.morale = morale
    if notes is not None:
        employee.notes = notes
    
    db.commit()
    db.refresh(employee)
    
    return {"status": "success", "employee": {"id": employee.id, "name": employee.name}}


@app.delete("/api/games/{game_id}/personnel/{employee_id}")
async def fire_personnel(
    game_id: str,
    employee_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dar de baja a un empleado (marcar como inactivo) y devolver el resultado."""
    employee = db.query(Personnel).filter(
        Personnel.id == employee_id,
        Personnel.game_id == game_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.is_active = False
    db.commit()
    
    return {"status": "success", "message": f"{employee.name} has been dismissed"}


# ===== TREASURY API =====

@app.get("/api/games/{game_id}/treasury")
async def get_treasury(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener información de la tesorería.

    Devuelve saldo actual, dificultad, reputación y transacciones recientes.
    """
    game = GameState(game_id)
    
    # Calculate monthly salaries from personnel
    personnel = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.is_active == True
    ).all()
    total_salaries = sum(p.monthly_salary for p in personnel)
    
    return {
        "current_balance": game.state.get("treasury", 0),
        "difficulty": game.state.get("difficulty"),
        "reputation": game.state.get("reputation", 0),
        "monthly_expenses": {
            "salaries": total_salaries,
            "loans": 0,  # TODO: implement loans system
            "total": total_salaries
        },
        "recent_transactions": game.state.get("transactions", [])[-10:]  # Last 10
    }


@app.post("/api/games/{game_id}/treasury/transaction")
async def add_transaction(
    game_id: str,
    amount: int = Form(...),
    description: str = Form(...),
    category: str = Form("other"),
) -> Dict[str, Any]:
    """Añadir una transacción a la tesorería y actualizar el historial de transacciones del juego."""
    from datetime import datetime
    
    game = GameState(game_id)
    
    transaction = {
        "date": datetime.now().isoformat(),
        "amount": amount,
        "description": description,
        "category": category
    }
    
    # Add transaction to history
    if "transactions" not in game.state:
        game.state["transactions"] = []
    game.state["transactions"].append(transaction)
    
    # Update treasury balance
    game.state["treasury"] = game.state.get("treasury", 0) + amount
    
    game.save()
    
    return {
        "status": "success",
        "new_balance": game.state["treasury"],
        "transaction": transaction
    }


# ===== MISSIONS MANAGEMENT API =====

@app.get("/api/games/{game_id}/missions")
async def get_missions(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener todas las misiones de un juego, separadas por estado.

    Devuelve un diccionario con las listas `active`, `completed` y `failed`.
    """
    missions = db.query(Mission).filter(Mission.game_id == game_id).all()
    
    active = []
    completed = []
    failed = []
    
    for mission in missions:
        mission_data = {
            "id": mission.id,
            "mission_type": mission.mission_type,
            "origin_world": mission.origin_world,
            "execution_place": mission.execution_place,
            "max_date": mission.max_date,
            "result": mission.result,
            "created_date": mission.created_date,
            "completed_date": mission.completed_date,
            "notes": mission.notes
        }
        
        # Add type-specific fields
        if mission.mission_type == "campaign":
            mission_data["objective_number"] = mission.objective_number
        else:
            mission_data["mission_code"] = mission.mission_code
            mission_data["book_page"] = mission.book_page
        
        # Categorize by result
        if mission.result == "exito":
            completed.append(mission_data)
        elif mission.result == "fracaso":
            failed.append(mission_data)
        else:
            active.append(mission_data)
    
    return {
        "active": active,
        "completed": completed,
        "failed": failed,
        "total": len(missions)
    }


@app.post("/api/games/{game_id}/missions")
async def create_mission(
    game_id: str,
    mission_type: str = Form(...),
    origin_world: str = Form(""),
    execution_place: str = Form(...),
    max_date: str = Form(""),
    notes: str = Form(""),
    # Campaign-specific
    objective_number: Optional[int] = Form(None),
    # Special mission-specific
    mission_code: Optional[str] = Form(None),
    book_page: Optional[int] = Form(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Crear una nueva misión (objetivo de campaña o misión especial).

    Valida los campos requeridos según `mission_type` y programa un evento
    de fecha límite si se proporciona `max_date`.
    """
    from datetime import date
    
    # Validate mission type
    if mission_type not in ["campaign", "special"]:
        raise HTTPException(status_code=400, detail="Mission type must be 'campaign' or 'special'")
    
    # Validate required fields for each type
    if mission_type == "campaign" and objective_number is None:
        raise HTTPException(status_code=400, detail="objective_number required for campaign missions")
    
    if mission_type == "special" and (not mission_code or book_page is None):
        raise HTTPException(status_code=400, detail="mission_code and book_page required for special missions")
    
    # Create mission
    mission = Mission(
        game_id=game_id,
        mission_type=mission_type,
        origin_world=origin_world,
        execution_place=execution_place,
        max_date=max_date,
        created_date=date.today().isoformat(),
        notes=notes,
        objective_number=objective_number,
        mission_code=mission_code,
        book_page=book_page
    )
    
    db.add(mission)
    db.commit()
    db.refresh(mission)
    
    # Log mission creation
    from app.event_logger import EventLogger
    game = GameState(game_id)
    
    if mission_type == "campaign":
        mission_desc = f"Objetivo #{objective_number} de campaña"
    else:
        mission_desc = f"Misión especial {mission_code} (pág. {book_page})"
    
    EventLogger._log_to_game(
        game,
        f"🎯 Nueva misión: {mission_desc} en {execution_place}",
        event_type="info"
    )
    
    # ========== CREATE MISSION DEADLINE EVENT IF NEEDED ==========
    if max_date:
        from app.time_manager import EventQueue
        
        game.state["event_queue"] = EventQueue.add_event(
            game.state.get("event_queue", []),
            "mission_deadline",
            max_date,
            {
                "mission_id": mission.id,
                "mission_type": mission_type,
                "objective": mission_desc
            }
        )
        game.save()
        
        EventLogger._log_to_game(
            game,
            f"📅 Fecha límite de misión programada: {max_date}",
            event_type="info"
        )
    # ========== END MISSION DEADLINE EVENT ==========
    
    return {
        "status": "success",
        "mission_id": mission.id,
        "mission_type": mission_type
    }


@app.put("/api/games/{game_id}/missions/{mission_id}")
async def update_mission_result(
    game_id: str,
    mission_id: int,
    result: str = Form(...),
    completed_date: str = Form(""),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
 ) -> Dict[str, Any]:
    """Actualizar el resultado de una misión (marcar como éxito o fracaso)."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.game_id == game_id
    ).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if result not in ["exito", "fracaso", ""]:
        raise HTTPException(status_code=400, detail="Result must be 'exito', 'fracaso', or empty")
    
    mission.result = result
    if completed_date:
        mission.completed_date = completed_date
    if notes is not None:
        mission.notes = notes
    
    db.commit()
    
    return {
        "status": "success",
        "mission_id": mission.id,
        "result": result
    }


@app.post("/api/games/{game_id}/missions/{mission_id}/resolve")
async def resolve_mission_deadline(
    game_id: str,
    mission_id: int,
    success: bool = Form(...),
    db: Session = Depends(get_db)
 ) -> Dict[str, Any]:
    """Resolver la fecha límite de una misión.

    `success` indica si la misión se considera completada con éxito o no.
    """
    from app.time_manager import GameCalendar
    
    game = GameState(game_id)
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.game_id == game_id
    ).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Get current game date
    current_date = GameCalendar.date_to_string(
        game.state.get('year', 1),
        game.state.get('month', 1),
        game.state.get('day', 1)
    )
    
    # Update mission status
    mission.result = "exito" if success else "fracaso"
    mission.completed_date = current_date
    
    # Update reputation based on success
    if success:
        game.state["reputation"] = game.state.get("reputation", 0) + 1
    else:
        game.state["reputation"] = max(0, game.state.get("reputation", 0) - 1)
    
    # Remove mission_deadline event from queue
    game.state["event_queue"] = [
        e for e in game.state.get("event_queue", [])
        if not (e["type"] == "mission_deadline" and e["data"]["mission_id"] == mission_id)
    ]
    
    game.save()
    db.commit()
    
    # Log result
    from app.event_logger import EventLogger
    
    if mission.mission_type == "campaign":
        mission_desc = f"Objetivo #{mission.objective_number}"
    else:
        mission_desc = f"Misión {mission.mission_code}"
    
    result_text = "completada con éxito ✅" if success else "fallida ❌"
    EventLogger._log_to_game(
        game,
        f"🎯 Misión {result_text}: {mission_desc}. Reputación: {game.state.get('reputation', 0)}",
        event_type="success" if success else "warning"
    )
    
    return {
        "status": "resolved",
        "success": success,
        "new_reputation": game.state.get("reputation", 0),
        "mission_result": mission.result
    }


@app.delete("/api/games/{game_id}/missions/{mission_id}")
async def delete_mission(
    game_id: str,
    mission_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Eliminar una misión de la base de datos y devolver el estado de la eliminación."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.game_id == game_id
    ).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    db.delete(mission)
    db.commit()
    
    return {"status": "success", "deleted_id": mission_id}


# ===== HIRING SYSTEM API =====

@app.get("/api/games/{game_id}/hire/available-positions")
async def get_available_positions(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener posiciones disponibles para contratación según el nivel tecnológico del planeta.

    Devuelve una lista de posiciones filtrada por `POSITIONS_CATALOG` y
    `TECH_LEVEL_REQUIREMENTS`.
    """
    game = GameState(game_id)
    current_planet_code = game.state.get("current_planet_code")
    
    if not current_planet_code:
        return {"positions": [], "error": "No current planet"}
    
    # Get planet tech level
    planet = db.query(Planet).filter(Planet.code == current_planet_code).first()
    if not planet or not planet.tech_level:
        return {"positions": [], "error": "Planet tech level not defined"}
    
    # Filter positions by tech level
    available = []
    for position_name, position_data in POSITIONS_CATALOG.items():
        required_level = position_data["tech_level"]
        if planet.tech_level in TECH_LEVEL_REQUIREMENTS.get(required_level, []):
            available.append({
                "name": position_name,
                "search_time_dice": position_data["search_time_dice"],
                "base_salary": position_data["base_salary"],
                "hire_threshold": position_data["hire_threshold"],
                "tech_level": required_level
            })
    
    return {
        "planet_code": current_planet_code,
        "planet_tech_level": planet.tech_level,
        "positions": available
    }


@app.post("/api/games/{game_id}/hire/start")
async def start_hire_search(
    game_id: str,
    position: str = Form(...),
    experience_level: str = Form(...),
    manual_dice_days: Optional[str] = Form(None),  # ← AÑADIR
    db: Session = Depends(get_db)
 ) -> Dict[str, Any]:
    """Iniciar búsqueda de contratación para el Director Gerente.

    Valida la petición, crea una `EmployeeTask` y programa su finalización
    si queda en primera posición de la cola.
    """
    
    # Validate position exists
    if position not in POSITIONS_CATALOG:
        raise HTTPException(status_code=400, detail="Invalid position")
    
    # Validate experience level
    if experience_level not in ["Novato", "Estándar", "Veterano"]:
        raise HTTPException(status_code=400, detail="Invalid experience level")
    
    # Get Director Gerente
    director = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.position == "Director gerente",
        Personnel.is_active == True
    ).first()
    
    if not director:
        raise HTTPException(status_code=404, detail="Director Gerente not found")
    
    # Calculate search days
    position_data = POSITIONS_CATALOG[position]
    # Procesar dados manuales si se proporcionan
    if manual_dice_days:
        try:
            days_dice = [int(x.strip()) for x in manual_dice_days.split(',')]
            if len(days_dice) != 2:
                raise ValueError("Se requieren 2 dados")
            if any(d < 1 or d > 6 for d in days_dice):
                raise ValueError("Dados deben estar entre 1 y 6")
        
            # Aplicar modificador de experiencia
            exp_mod = {'Novato': -1, 'Estándar': 0, 'Veterano': 1}.get(experience_level, 0)
            search_days = sum(days_dice) + exp_mod
            search_days = max(1, search_days)  # Mínimo 1 día
        except ValueError as e:
            raise HTTPException(400, f"Dados inválidos: {str(e)}")
    else:
        # Fallback automático (no debería usarse si frontend usa DiceRollerUI)
        dice_roller = DiceRoller()
        search_days = calculate_hire_time(
            position_data["search_time_dice"],
            experience_level,
            dice_roller
        )
    
    # Calculate salary
    final_salary = calculate_hire_salary(position_data["base_salary"], experience_level)
    
    # Determine queue position
    existing_tasks = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game_id,
        EmployeeTask.employee_id == director.id,
        EmployeeTask.status.in_(["pending", "in_progress"])
    ).count()
    
    queue_position = existing_tasks + 1
    
    # Get current date
    game = GameState(game_id)
    current_date = GameCalendar.date_to_string(
        game.state.get('year', 1),
        game.state.get('month', 1),
        game.state.get('day', 1)
    )
    
    # Create task
    task = EmployeeTask(
        game_id=game_id,
        employee_id=director.id,
        task_type="hire_search",
        status="pending",
        queue_position=queue_position,
        task_data=json.dumps({
            "position": position,
            "experience_level": experience_level,
            "search_days": search_days,
            "base_salary": position_data["base_salary"],
            "final_salary": final_salary,
            "hire_threshold": position_data["hire_threshold"]
        }),
        created_date=current_date
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Log event for ALL hire searches (not just first in queue)
    from app.event_logger import EventLogger
    EventLogger._log_to_game(game, EventLogger.format_hire_start(position, experience_level, search_days))
    
    # If it's the first task, start it immediately
    if queue_position == 1:
        task.status = "in_progress"
        task.started_date = current_date
        task.completion_date = GameCalendar.add_days(current_date, search_days)
        
        # Add event to queue
        game.state["event_queue"] = EventQueue.add_event(
            game.state.get("event_queue", []),
            "task_completion",
            task.completion_date,
            {"task_id": task.id, "employee_id": director.id}
        )
        game.save()
        db.commit()
    
    return {
        "status": "success",
        "task_id": task.id,
        "queue_position": queue_position,
        "search_days": search_days,
        "final_salary": final_salary,
        "task_status": task.status
    }


@app.get("/api/games/{game_id}/personnel/{employee_id}/tasks")
async def get_employee_tasks(
    game_id: str,
    employee_id: int,
    db: Session = Depends(get_db)
 ) -> Dict[str, Any]:
    """Obtener todas las tareas de un empleado (principalmente Director Gerente)."""
    
    employee = db.query(Personnel).filter(
        Personnel.id == employee_id,
        Personnel.game_id == game_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    tasks = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game_id,
        EmployeeTask.employee_id == employee_id
    ).order_by(EmployeeTask.queue_position).all()
    
    current_task = None
    pending_tasks = []
    completed_tasks = []
    
    for task in tasks:
        task_data = json.loads(task.task_data) if task.task_data else {}
        
        task_info = {
            "id": task.id,
            "task_type": task.task_type,
            "status": task.status,
            "queue_position": task.queue_position,
            "task_data": task_data,
            "created_date": task.created_date,
            "started_date": task.started_date,
            "completion_date": task.completion_date,
            "finished_date": task.finished_date
        }
        
        if task.status == "in_progress":
            current_task = task_info
        elif task.status == "pending":
            pending_tasks.append(task_info)
        elif task.status in ["completed", "failed"]:
            result_data = json.loads(task.result_data) if task.result_data else {}
            task_info["result"] = result_data
            completed_tasks.append(task_info)
    
    return {
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "position": employee.position
        },
        "current_task": current_task,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "total_tasks": len(tasks)
    }


@app.put("/api/games/{game_id}/tasks/{task_id}/reorder")
async def reorder_task(
    game_id: str,
    task_id: int,
    new_position: int = Form(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Reordenar una tarea pendiente en la cola; ajusta las posiciones de las demás."""
    
    task = db.query(EmployeeTask).filter(
        EmployeeTask.id == task_id,
        EmployeeTask.game_id == game_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "pending":
        raise HTTPException(status_code=400, detail="Can only reorder pending tasks")
    
    # Get all pending tasks for this employee
    pending_tasks = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game_id,
        EmployeeTask.employee_id == task.employee_id,
        EmployeeTask.status == "pending"
    ).order_by(EmployeeTask.queue_position).all()
    
    # Validate new position
    if new_position < 2 or new_position > len(pending_tasks) + 1:
        raise HTTPException(status_code=400, detail="Invalid new position")
    
    old_position = task.queue_position
    
    # Reorder tasks
    if old_position < new_position:
        # Moving down
        for t in pending_tasks:
            if old_position < t.queue_position <= new_position:
                t.queue_position -= 1
    else:
        # Moving up
        for t in pending_tasks:
            if new_position <= t.queue_position < old_position:
                t.queue_position += 1
    
    task.queue_position = new_position
    db.commit()
    
    return {"status": "success", "new_position": new_position}


@app.delete("/api/games/{game_id}/tasks/{task_id}")
async def delete_task(
    game_id: str,
    task_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Eliminar una tarea pendiente y ajustar la cola en consecuencia."""
    
    task = db.query(EmployeeTask).filter(
        EmployeeTask.id == task_id,
        EmployeeTask.game_id == game_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "pending":
        raise HTTPException(status_code=400, detail="Can only delete pending tasks")
    
    employee_id = task.employee_id
    deleted_position = task.queue_position
    
    db.delete(task)
    
    # Adjust queue positions of remaining tasks
    remaining_tasks = db.query(EmployeeTask).filter(
        EmployeeTask.game_id == game_id,
        EmployeeTask.employee_id == employee_id,
        EmployeeTask.status == "pending",
        EmployeeTask.queue_position > deleted_position
    ).all()
    
    for t in remaining_tasks:
        t.queue_position -= 1
    
    db.commit()
    
    return {"status": "success", "deleted_id": task_id}


@app.post("/api/games/{game_id}/time/advance")
async def advance_time(
    game_id: str, 
    manual_dice: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Avanza el tiempo al próximo evento y lo procesa usando el sistema de handlers
    
    Sistema modular:
    - Cada tipo de evento tiene su propio handler
    - Main dispatcher simplemente llama al handler apropiado
    - Handler decide si el evento se borra de la cola
    """
    from app.event_handlers import get_event_handler
    
    game = GameState(game_id)
    event_queue = game.state.get("event_queue", [])
    
    # Check if there are events
    if not event_queue:
        return {"status": "no_events", "message": "No hay eventos pendientes"}
    
    # Get next event
    next_event = EventQueue.get_next_event(event_queue)
    if not next_event:
        return {"status": "no_events"}
    
    # Store old date
    old_date = GameCalendar.date_to_string(
        game.state.get('year', 1),
        game.state.get('month', 1),
        game.state.get('day', 1)
    )
    
    # Advance calendar to event date
    new_year, new_month, new_day = GameCalendar.parse_date(next_event["date"])
    game.state["year"] = new_year
    game.state["month"] = new_month
    game.state["day"] = new_day
    game.save()
    
    # Get handler for event type
    handler = get_event_handler(next_event["type"])
    
    if not handler:
        return {
            "status": "error",
            "message": f"No handler for event type: {next_event['type']}"
        }
    
    # Execute handler
    try:
        result = handler(next_event, game, db, manual_dice)
        
        # Remove from queue if handler says so
        if result.remove_from_queue:
            game.state["event_queue"] = EventQueue.remove_event(
                game.state.get("event_queue", []),
                next_event
            )
            game.save()
        
        db.commit()
        
        # Return result
        return {
            "status": "success",
            "old_date": old_date,
            "new_date": next_event["date"],
            "event_result": result.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }


# ===== SETUP COMPLETION WITH DIFFICULTY =====

@app.post("/api/games/{game_id}/complete-setup")
async def complete_setup(
    game_id: str,
    difficulty: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Complete game setup with difficulty selection
    
    This creates initial personnel and sets starting treasury
    """
    from datetime import date
    
    game = GameState(game_id)
    
    # Validate difficulty
    difficulty_funds = {
        "easy": 600,
        "normal": 500,
        "hard": 400
    }
    
    if difficulty not in difficulty_funds:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")
    
    # Set difficulty and initial funds
    game.state["difficulty"] = difficulty
    game.state["treasury"] = difficulty_funds[difficulty]
    game.state["reputation"] = 0
    game.state["setup_complete"] = True
    game.save()
    
    # Log game start with more immersive details
    from app.event_logger import EventLogger
    company_name = game.state.get("company_name", "Compañía Desconocida")
    ship_name = game.state.get("ship_name", "Nave Sin Nombre")
    current_planet = game.state.get("current_planet_code", "???")
    
    EventLogger._log_to_game(
        game,
        f"📜 La empresa {company_name} inicia sus operaciones con la nave {ship_name} desde el planeta {current_planet}. "
        f"Dificultad: {difficulty.upper()}. Fondos iniciales: {difficulty_funds[difficulty]} SC",
        event_type="success"
    )
    
    # Create initial personnel
    hire_date = date.today().isoformat()
    
    for emp_data in INITIAL_PERSONNEL:
        employee = Personnel(
            game_id=game_id,
            position=emp_data["position"],
            name=emp_data["name"],
            monthly_salary=emp_data["salary"],
            experience=emp_data["exp"],
            morale=emp_data["morale"],
            hire_date=hire_date,
            is_active=True
        )
        db.add(employee)
    
    db.commit()
    
    # Log initial personnel
    for emp_data in INITIAL_PERSONNEL:
        EventLogger._log_to_game(
            game,
            f"👥 {emp_data['name']} se une como {emp_data['position']} por {emp_data['salary']} SC/mes",
            event_type="info"
        )
    
    # Calculate total salaries
    total_salaries = sum(emp["salary"] for emp in INITIAL_PERSONNEL)
    
    # ========== CREATE INITIAL SALARY PAYMENT EVENT ==========
    from app.time_manager import GameCalendar, EventQueue
    
    current_date = GameCalendar.date_to_string(
        game.state.get('year', 1),
        game.state.get('month', 1),
        game.state.get('day', 1)
    )
    
    # Create first salary payment event for day 35
    next_salary_date = GameCalendar.next_day_35(current_date)
    
    if "event_queue" not in game.state:
        game.state["event_queue"] = []
    
    game.state["event_queue"] = EventQueue.add_event(
        game.state.get("event_queue", []),
        "salary_payment",
        next_salary_date,
        {"monthly_payment": True}
    )
    game.save()
    
    EventLogger._log_to_game(
        game,
        f"📅 Próximo pago de salarios programado para el día 35 ({next_salary_date})",
        event_type="info"
    )
    # ========== END SALARY PAYMENT EVENT ==========
    
    return {
        "status": "success",
        "difficulty": difficulty,
        "starting_funds": difficulty_funds[difficulty],
        "personnel_count": len(INITIAL_PERSONNEL),
        "monthly_salaries": total_salaries
    }


# ===== PASSENGER TRANSPORT API =====

@app.get("/api/games/{game_id}/passenger-transport/info")
async def get_passenger_transport_info(
    game_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get info for passenger transport action
    Returns capacity, current passengers, and modifiers
    """
    from app.ship_data import get_ship_stats
    
    game = GameState(game_id)
    ship_stats = get_ship_stats(game.state.get("ship_model", "Basic Starfall"))
    
    # 1. Ship Capacity
    ship_capacity = ship_stats.get("passengers", 10)
    current_passengers = game.state.get("passengers", 0)
    
    # 2. Planet Info (Average Passengers)
    planet_code = game.state.get("current_planet_code")
    avg_passengers = 0
    if planet_code:
        planet = db.query(Planet).filter(Planet.code == planet_code).first()
        if planet:
            avg_passengers = planet.max_passengers
            
    # 3. Check for modifiers (Personnel)
    # Manager: "Responsable de soporte a pasajeros"
    manager = db.query(Personnel).filter(
        Personnel.game_id == game_id, 
        Personnel.position == "Responsable de soporte a pasajeros",
        Personnel.is_active == True
    ).first()
    
    manager_bonus = 0
    if manager:
        # Experience: N(-1), E(0), V(+1) -> Matches standard rule, but let's be explicit if needed
        # Actually standard rule: N(-1), E(0), V(+1) 
        # Moral: B(-1), M(0), A(+1)
        # Reputation / 2
        
        exp_mod = {"N": -1, "E": 0, "V": 1}.get(manager.experience, 0)
        morale_mod = {"B": -1, "M": 0, "A": 1}.get(manager.morale, 0)
        rep_mod = math.floor(game.state.get("reputation", 0) / 2) # Reputación / 2
        
        manager_bonus = exp_mod + morale_mod + rep_mod
        
    # Flight Attendants: "Auxiliar de vuelo"
    flight_attendants = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.position == "Auxiliar de vuelo",
        Personnel.is_active == True
    ).all()
    
    attendants_count = len(flight_attendants)
    
    return {
        "ship_capacity": ship_capacity,
        "current_passengers": current_passengers,
        "planet_avg_passengers": avg_passengers,
        "modifiers": {
            "has_manager": manager is not None,
            "manager_name": manager.name if manager else None,
            "manager_bonus": manager_bonus,
            "attendants_count": attendants_count
        },
        "location": game.state.get("ship_location_on_planet", "Mundo"),
        "available": game.state.get("passenger_transport_available", True)
    }


@app.post("/api/games/{game_id}/passenger-transport/execute")
async def execute_passenger_transport(
    game_id: str,
    manual_dice: Optional[str] = Form(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute passenger transport action
    
    1. Roll 2d6 (+ modifiers from Manager)
    2. Determine outcome (<7, 7-9, 10-12) -> Number of passengers
    3. Update Manager stats (Moral/XP) via personnel_manager
    4. Calculate Revenue (Base x Attendants multiplier + Attendants XP bonus)
    5. Update Game State (Treasury, Passengers)
    """
    from app.personnel_manager import update_employee_roll_stats
    from app.ship_data import get_ship_stats
    from app.event_logger import EventLogger
    
    game = GameState(game_id)
    
    # --- 1. Basic Checks ---
    if not game.state.get("passenger_transport_available", True):
        raise HTTPException(400, "Transporte de pasajeros ya realizado en esta visita. Debes viajar a otro cuadrante y volver.")

    planet_code = game.state.get("current_planet_code")
    planet = db.query(Planet).filter(Planet.code == planet_code).first()
    if not planet:
        raise HTTPException(400, "Not on a known planet")
        
    avg_passengers = planet.max_passengers
    ship_stats = get_ship_stats(game.state.get("ship_model", "Basic Starfall"))
    ship_capacity = ship_stats.get("passengers", 10)
    
    # --- 2. Calculate Modifiers ---
    manager = db.query(Personnel).filter(
        Personnel.game_id == game_id, 
        Personnel.position == "Responsable de soporte a pasajeros",
        Personnel.is_active == True
    ).first()
    
    total_mod = 0
    mods_detail = {}
    
    if manager:
        exp_mod = {"N": -1, "E": 0, "V": 1}.get(manager.experience, 0)
        morale_mod = {"B": -1, "M": 0, "A": 1}.get(manager.morale, 0)
        rep_mod = math.floor(game.state.get("reputation", 0) / 2)
        
        total_mod = exp_mod + morale_mod + rep_mod
        mods_detail = {"experience": exp_mod, "morale": morale_mod, "reputation_half": rep_mod}
    
    # --- 3. Roll Dice ---
    if manual_dice and manual_dice.strip():
        dice_values = [int(x.strip()) for x in manual_dice.split(",")]
        is_manual = True
    else:
        dice_values = DiceRoller.roll_dice(2, 6)
        is_manual = False
        
    dice_sum = sum(dice_values)
    final_result = dice_sum + total_mod
    
    # --- 4. Determine Passengers Boarded ---
    # < 7: Half avg (round down)
    # 7-9: Avg
    # 10-12+: Double avg
    
    if final_result < 7:
        raw_passengers = math.floor(avg_passengers / 2)
        outcome_type = "low"
    elif final_result <= 9:
        raw_passengers = avg_passengers
        outcome_type = "mid"
    else:
        raw_passengers = avg_passengers * 2
        outcome_type = "high"
        
    # Cap at ship capacity
    boarding_passengers = min(int(raw_passengers), ship_capacity)
    
    # --- 5. Update Personnel Stats (Manager) --
    personnel_changes = None
    if manager:
        personnel_changes = update_employee_roll_stats(manager, dice_values, final_result)
        # Log personnel changes
        for msg in personnel_changes["messages"]:
            EventLogger._log_to_game(game, f"👔 {manager.name}: {msg}", "info")
            
    # --- 6. Calculate Revenue ---
    # Base: Flight Attendants Count
    # 3 Aux -> x4 SC
    # 2 Aux -> x3 SC
    # 1 Aux -> x2 SC
    # 0 Aux -> x1 SC
    
    flight_attendants = db.query(Personnel).filter(
        Personnel.game_id == game_id,
        Personnel.position == "Auxiliar de vuelo",
        Personnel.is_active == True
    ).all()
    
    num_aux = len(flight_attendants)
    if num_aux >= 3:
        multiplier = 4
    elif num_aux == 2:
        multiplier = 3
    elif num_aux == 1:
        multiplier = 2
    else:
        multiplier = 1
        
    base_revenue = boarding_passengers * multiplier
    
    # Adjustments: -5 per Novice Aux, +5 per Veteran Aux
    novice_penalty = sum(5 for a in flight_attendants if a.experience == "N")
    veteran_bonus = sum(5 for a in flight_attendants if a.experience == "V")
    
    final_revenue = base_revenue - novice_penalty + veteran_bonus
    final_revenue = max(0, final_revenue) # No negative revenue
    
    # --- 7. Update Game State ---
    game.state["passengers"] = boarding_passengers
    
    # Add to treasury
    game.state["treasury"] += final_revenue
    
    # Log Transaction
    if "transactions" not in game.state:
        game.state["transactions"] = []
    
    game.state["transactions"].append({
        "date": GameCalendar.date_to_string(game.state.get("year", 1), game.state.get("month", 1), game.state.get("day", 1)),
        "amount": final_revenue,
        "category": "comercio", # or "transporte"
        "description": f"Transporte de {boarding_passengers} pasajeros"
    })
    
    game.record_dice_roll(2, dice_values, is_manual, "passenger_transport")
    game.save()
    db.commit()
    
    # Log Event
    EventLogger._log_to_game(
        game, 
        f"✈️ Embarque de Pasajeros: {boarding_passengers} pax. Ingresos: {final_revenue} SC.",
        "success" if final_revenue > 0 else "info"
    )

    return {
        "status": "success",
        "dice": dice_values,
        "modifiers": mods_detail,
        "total_roll": final_result,
        "outcome": outcome_type, # low/mid/high
        "passengers": {
            "calculated": raw_passengers,
            "boarded": boarding_passengers,
            "capacity": ship_capacity
        },
        "revenue": {
            "base": base_revenue,
            "multiplier": multiplier,
            "novice_penalty": novice_penalty,
            "veteran_bonus": veteran_bonus,
            "total": final_revenue
        },
        "personnel_changes": personnel_changes
    }

# ===== TRADING API =====

@app.get("/api/games/{game_id}/trade/market")
async def get_trade_market(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener productos disponibles para comprar y órdenes activas."""
    from app.trade_manager import TradeManager
    
    game = GameState(game_id)
    planet_code = game.state.get("current_planet_code")
    if not planet_code:
        raise HTTPException(status_code=400, detail="Ship not on a planet")
        
    manager = TradeManager(game_id, db)
    market_data = manager.get_market_data(planet_code)
    
    return market_data

@app.get("/api/games/{game_id}/trade/orders")
async def get_trade_orders(game_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtener todas las órdenes de comercio (libro de operaciones)."""
    from app.database import TradeOrder
    
    orders = db.query(TradeOrder).filter(TradeOrder.game_id == game_id).all()
    # TODO: Format nicely
    return {"orders": orders}

@app.post("/api/games/{game_id}/trade/negotiate")
async def negotiate_trade(
    game_id: str,
    action: str = Form(...), # "buy" or "sell"
    manual_roll: Optional[int] = Form(None)
) -> Dict[str, Any]:
    """Simular la tirada de negociación.

    Devuelve modificadores y resultados pero NO ejecuta la transacción.
    """
    from app.trade_manager import TradeManager
    
    game = GameState(game_id)
    # Mock Negotiator skill for now (or fetch from DB)
    negotiator_skill = 0 
    reputation = game.state.get("reputation", 0)
    
    # We need a dummy session or refactor TradeManager to not always need DB just for math
    # TradeManager currently takes DB in init. We can pass None if just doing math, 
    # but let's grab one if possible, or just instantiate lightweight?
    # Actually negotiate_price doesn't need DB.
    # We'll use a local db session context if we really need it, but here we can just pass None safely 
    # IF negotiate_price doesn't access db.
    # Checking code: `negotiate_price` uses `DiceRoller` and simple math. Safe.
    
    manager = TradeManager(game_id, None) 
    result = manager.negotiate_price(
        negotiator_skill=negotiator_skill, 
        reputation=reputation, 
        is_buy=(action == "buy"),
        manual_roll=manual_roll
    )
    
    return result

@app.post("/api/games/{game_id}/trade/buy")
async def execute_trade_buy(
    game_id: str,
    planet_code: int = Form(...),
    product_code: str = Form(...),
    quantity: int = Form(...),
    unit_price: int = Form(...),
    traceability: bool = Form(True),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ejecutar una transacción de compra."""
    from app.trade_manager import TradeManager
    
    manager = TradeManager(game_id, db)
    result = manager.execute_buy(
        planet_code=planet_code,
        product_code=product_code,
        quantity=quantity,
        unit_price=unit_price,
        traceability=traceability
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result

@app.post("/api/games/{game_id}/trade/sell")
async def execute_trade_sell(
    game_id: str,
    order_id: int = Form(...),
    planet_code: int = Form(...),
    sell_price_total: int = Form(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ejecutar una transacción de venta."""
    from app.trade_manager import TradeManager
    
    manager = TradeManager(game_id, db)
    result = manager.execute_sell(
        order_id=order_id,
        planet_code=planet_code,
        sell_price_total=sell_price_total
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result
