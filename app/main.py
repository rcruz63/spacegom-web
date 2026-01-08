from fastapi import FastAPI, Form, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import random

from app.database import get_db, Planet, init_db
from app.game_state import GameState
from app.dice import DiceRoller
from app.name_suggestions import get_random_company_name, get_random_ship_name

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
templates.env.globals.update(chr=chr)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# ===== WEB PAGES =====

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    return templates.TemplateResponse("setup.html", {"request": request})


# ===== GAME MANAGEMENT API =====

@app.get("/api/games")
async def list_games():
    """List all available games"""
    games = GameState.list_games()
    return {"games": games}

@app.post("/api/games/new")
async def create_game(game_name: Optional[str] = Form(None)):
    """Create a new game"""
    game = GameState.create_new_game(game_name)
    game.save()
    return {"game_id": game.game_id, "state": game.state}

@app.get("/api/games/{game_id}")
async def get_game_state(game_id: str):
    """Get current game state"""
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
):
    """Update game state fields"""
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


@app.post("/api/games/{game_id}/update-location")
async def update_ship_location(
    game_id: str,
    location: str = Form(...)
):
    """
    Update ship location on the planet (Mundo, Espaciopuerto, etc.)
    """
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
):
    """
    Save player company and ship details
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
):
    """
    Initial company placement setup
    
    Step 1: Roll 2d6 for space area (2-12)
    Step 2: Roll 2d6 for world density and determine level
           - 2-4: Baja
           - 5-9: Media  
           - 10-12: Alta
    
    Args:
        area_manual: Optional comma-separated manual 2d6 results
        density_manual: Optional comma-separated manual 2d6 results
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
):
    """
    Initial ship position setup
    Roll 1d6 for row (1-6) and 1d6 for col (1-6)
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
    
    # Update game state (offset 0-5 for internal grid if needed, but keeping 1-6 as per user request)
    game.state["ship_row"] = row_val
    game.state["ship_col"] = col_val
    game.state["ship_pos_complete"] = True
    
    # First exploration of current quadrant
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
):
    """Update missing planet data for bootstrap validation"""
    planet = db.query(Planet).filter(Planet.code == code).first()
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {code} not found")
    
    planet.tech_level = tech_level
    planet.population_over_1000 = population_over_1000
    db.commit()
    
    return {"status": "success", "planet": {"code": code, "tech_level": tech_level, "population_over_1000": population_over_1000}}


# ===== DICE ROLLING API =====

@app.post("/api/roll-dice", response_class=HTMLResponse)
async def roll_dice(request: Request, num_dices: int = Form(1), manual_result: str | None = Form(None)):
    """Roll dice (for HTMX component - legacy endpoint)"""
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

@app.post("/api/games/{game_id}/roll")
async def roll_dice_json(
    game_id: str,
    num_dice: int = Form(1),
    manual_results: Optional[str] = Form(None),
    purpose: str = Form("")
):
    """
    Roll dice and record in game history
    
    Args:
        num_dice: Number of dice to roll (1-10)
        manual_results: Optional comma-separated manual results (e.g., "4,6,6")
        purpose: Purpose of the roll (e.g., "planet_code", "combat", "negotiation")
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
):
    """
    Roll 3 dice to generate a planet code and fetch planet data
    
    Args:
        manual_results: Optional comma-separated manual results (e.g., "4,6,6")
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
    """
    Format planet data for API responses using new schema
    
    Args:
        planet: Planet object from database
        
    Returns:
        Formatted dictionary with all planet information
    """
    return {
        "code": planet.code,
        "name": planet.name,
        "life_support": {
            "type": planet.life_support,
            "local_contagion_risk": planet.local_contagion_risk,
            "days_to_hyperspace": planet.days_to_hyperspace,
            "legal_order_threshold": planet.legal_order_threshold
        },
        "spaceport": {
            "quality": planet.spaceport_quality,
            "fuel_density": planet.fuel_density,
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
async def get_planet(code: int, db: Session = Depends(get_db)):
    """Get planet by code"""
    planet = db.query(Planet).filter(Planet.code == code).first()
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {code} not found")
    
    return {
        "planet": format_planet_data(planet),
        "is_valid_start": is_valid_starting_planet(planet)
    }

@app.get("/api/planets")
async def search_planets(name: Optional[str] = None, db: Session = Depends(get_db)):
    """Search planets by name"""
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
async def set_starting_planet(game_id: str, code: int = Form(...)):
    """Set the starting planet for the game"""
    game = GameState(game_id)
    game.state["current_planet_code"] = code
    game.state["starting_planet_code"] = code
    
    # Also record it in the current quadrant
    row = game.state.get("ship_row")
    col = game.state.get("ship_col")
    if row and col:
        game.discover_planet(row, col, code)
        # Mark as explored as well
        game.explore_quadrant(row, col)
        
    game.save()
    return {"status": "success", "code": code}



@app.get("/api/planets/next/{current_code}")
async def get_next_planet(current_code: int, db: Session = Depends(get_db)):
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
):
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
async def suggest_company_name():
    """
    Retorna un nombre de compañía aleatorio desde el CSV
    
    Returns:
        JSON con el nombre sugerido
    """
    return {"name": get_random_company_name()}


@app.get("/api/suggestions/ship-name")
async def suggest_ship_name():
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
):
    """Mark a quadrant as explored"""
    game = GameState(game_id)
    game.explore_quadrant(row, col)
    
    return {
        "explored": True,
        "quadrant": f"{row},{col}",
        "explored_quadrants": game.state["explored_quadrants"]
    }

