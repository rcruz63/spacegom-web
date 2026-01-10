from fastapi import FastAPI, Form, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
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

@app.get("/personnel", response_class=HTMLResponse)
async def personnel_page(request: Request):
    return templates.TemplateResponse("personnel.html", {"request": request})

@app.get("/treasury", response_class=HTMLResponse)
async def treasury_page(request: Request):
    return templates.TemplateResponse("treasury.html", {"request": request})

@app.get("/missions", response_class=HTMLResponse)
async def missions_page(request: Request):
    return templates.TemplateResponse("missions.html", {"request": request})


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
    Format planet data for API responses using decoded human-readable values
    
    Args:
        planet: Planet object from database
        
    Returns:
        Formatted dictionary with all planet information (codes + descriptions)
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

# ===== PERSONNEL API =====

@app.get("/api/games/{game_id}/personnel")
async def get_personnel(game_id: str, db: Session = Depends(get_db)):
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
):
    """Hire new personnel"""
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
):
    """Update personnel information"""
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
):
    """Fire personnel (mark as inactive)"""
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
async def get_treasury(game_id: str, db: Session = Depends(get_db)):
    """Get treasury information"""
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
):
    """Add a treasury transaction"""
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
async def get_missions(game_id: str, db: Session = Depends(get_db)):
    """Get all missions for a game, separated by status"""
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
):
    """Create a new mission (campaign objective or special mission)"""
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
):
    """Update mission result (mark as success or failure)"""
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


@app.delete("/api/games/{game_id}/missions/{mission_id}")
async def delete_mission(
    game_id: str,
    mission_id: int,
    db: Session = Depends(get_db)
):
    """Delete a mission"""
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
async def get_available_positions(game_id: str, db: Session = Depends(get_db)):
    """Get positions available for hiring based on current planet's tech level"""
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
    db: Session = Depends(get_db)
):
    """Start a new hire search task for the Director Gerente"""
    
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
    current_date = f"{game.state.get('year', 1)}-{game.state.get('month', 1):02d}-{game.state.get('day', 1):02d}"
    
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
):
    """Get all tasks for an employee (mainly Director Gerente)"""
    
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
):
    """Reorder a pending task in the queue"""
    
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
):
    """Delete a pending task"""
    
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
    """Advance time to the next event and process it"""
    
    game = GameState(game_id)
    event_queue = game.state.get("event_queue", [])
    
    if not event_queue:
        return {"status": "no_events", "message": "No hay eventos pendientes"}
    
    # Get next event
    next_event = EventQueue.get_next_event(event_queue)
    if not next_event:
        return {"status": "no_events"}
    
    # Advance to event date
    old_date = f"{game.state.get('year', 1)}-{game.state.get('month', 1):02d}-{game.state.get('day', 1):02d}"
    new_year, new_month, new_day = GameCalendar.parse_date(next_event["date"])
    
    game.state["year"] = new_year
    game.state["month"] = new_month
    game.state["day"] = new_day
    
    # Process event based on type
    event_result = {}
    
    if next_event["type"] == "task_completion":
        # Resolve hire task
        task_id = next_event["data"]["task_id"]
        task = db.query(EmployeeTask).get(task_id)
        
        if task and task.status == "in_progress":
            task_data = json.loads(task.task_data)
            
            # Get Director Gerente
            director = db.query(Personnel).get(task.employee_id)
            
            # Calculate modifiers
            exp_mod = {"N": -1, "E": 0, "V": 1}.get(director.experience, 0)
            morale_mod = {"B": -1, "M": 0, "A": 1}.get(director.morale, 0)
            rep_mod = game.state.get("reputation", 0)
            total_mod = exp_mod + morale_mod + rep_mod
            
            
            # Roll 2d6 (or use manual values)
            if manual_dice:
                dice_values = [int(x) for x in manual_dice.split(',')]
            else:
                dice_roller = DiceRoller()
                dice_values = dice_roller.roll_dice(2, 6)
            dice_sum = sum(dice_values)
            final_result = dice_sum + total_mod
            
            # Check success
            threshold = task_data["hire_threshold"]
            success = final_result >= threshold
            
            # Update employee evolution
            if final_result >= 10:
                # Increase morale
                if director.morale == "B":
                    director.morale = "M"
                elif director.morale == "M":
                    director.morale = "A"
            elif final_result <= 4:
                # Decrease morale
                if director.morale == "A":
                    director.morale = "M"
                elif director.morale == "M":
                    director.morale = "B"
            
            # Check for double 6 (experience increase)
            if dice_values[0] == 6 and dice_values[1] == 6:
                if director.experience == "N":
                    director.experience = "E"
                elif director.experience == "E":
                    director.experience = "V"
            
            new_employee_id = None
            if success:
                # Create new employee
                from app.name_suggestions import get_random_personal_name
                
                new_employee = Personnel(
                    game_id=game_id,
                    position=task_data["position"],
                    name=get_random_personal_name(),
                    monthly_salary=task_data["final_salary"],
                    experience=task_data["experience_level"][0],  # N, E, V
                    morale="M",  # Always start with Medium morale
                    hire_date=next_event["date"],
                    is_active=True,
                    notes="Contratado automáticamente"
                )
                db.add(new_employee)
                db.flush()  # Get ID
                new_employee_id = new_employee.id
            
            # Update task
            task.status = "completed" if success else "failed"
            task.finished_date = next_event["date"]
            task.result_data = json.dumps({
                "dice_values": dice_values,
                "dice_sum": dice_sum,
                "modifiers": {
                    "experience": exp_mod,
                    "morale": morale_mod,
                    "reputation": rep_mod,
                    "total": total_mod
                },
                "final_result": final_result,
                "threshold": threshold,
                "success": success,
                "employee_id": new_employee_id
            })
            
            event_result = {
                "type": "hire_resolution",
                "position": task_data["position"],
                "experience_level": task_data["experience_level"],
                "dice": dice_values,
                "modifiers": {
                    "experience": exp_mod,
                    "morale": morale_mod,
                    "reputation": rep_mod,
                    "total": total_mod
                },
                "total": final_result,
                "threshold": threshold,
                "success": success,
                "new_employee_id": new_employee_id,
                "director_evolution": {
                    "old_morale": director.morale,
                    "old_experience": director.experience
                }
            }
            
            # Reorganize queue and start next task
            remaining_tasks = db.query(EmployeeTask).filter(
                EmployeeTask.game_id == game_id,
                EmployeeTask.employee_id == task.employee_id,
                EmployeeTask.status == "pending"
            ).order_by(EmployeeTask.queue_position).all()
            
            for t in remaining_tasks:
                t.queue_position -= 1
            
            # Start next task if exists
            if remaining_tasks:
                next_task = remaining_tasks[0]  # Now position 1
                next_task.status = "in_progress"
                next_task.started_date = next_event["date"]
                
                task_data_next = json.loads(next_task.task_data)
                next_task.completion_date = GameCalendar.add_days(
                    next_event["date"],
                    task_data_next["search_days"]
                )
                
                # Add new event
                game.state["event_queue"] = EventQueue.add_event(
                    game.state.get("event_queue", []),
                    "task_completion",
                    next_task.completion_date,
                    {"task_id": next_task.id, "employee_id": task.employee_id}
                )
                
                event_result["next_task_started"] = {
                    "task_id": next_task.id,
                    "position": task_data_next["position"],
                    "completion_date": next_task.completion_date
                }
    
    # Remove processed event
    game.state["event_queue"] = EventQueue.remove_event(event_queue, next_event)
    
    db.commit()
    game.save()
    
    return {
        "status": "success",
        "old_date": old_date,
        "new_date": next_event["date"],
        "event_type": next_event["type"],
        "event_result": event_result,
        "next_event": EventQueue.get_next_event(game.state.get("event_queue", []))
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
    
    # Calculate total salaries
    total_salaries = sum(emp["salary"] for emp in INITIAL_PERSONNEL)
    
    return {
        "status": "success",
        "difficulty": difficulty,
        "starting_funds": difficulty_funds[difficulty],
        "personnel_count": len(INITIAL_PERSONNEL),
        "monthly_salaries": total_salaries
    }
