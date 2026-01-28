"""
Routes para gestión de planetas.

Este módulo contiene los endpoints relacionados con:
- Consulta de planetas por código o nombre
- Tirada de código de planeta (3d6)
- Actualización de notas y datos de bootstrap
- Sugerencias de nombres
"""
from fastapi import APIRouter, Form, HTTPException
from typing import Optional, Dict, Any

from app.planets_repo import (
    Planet,
    get_planet_by_code,
    search_planets as repo_search_planets,
    update_planet_notes as repo_update_planet_notes,
    update_planet_bootstrap as repo_update_planet_bootstrap,
)
from app.game_state import GameState
from app.dice import DiceRoller
from app.name_suggestions import get_random_company_name, get_random_ship_name

router = APIRouter(tags=["planets"])


# ===== HELPER FUNCTIONS =====

def format_planet_data(planet: Planet) -> Dict[str, Any]:
    """
    Formatea los datos de un planeta para respuestas de API.
    
    Convierte códigos internos a descripciones legibles usando funciones
    de utils.py y estructura los datos en secciones lógicas.
    
    Args:
        planet: Instancia de Planet obtenida de la base de datos
    
    Returns:
        Diccionario estructurado con:
        - code, name
        - life_support: Información completa de soporte vital
        - spaceport: Datos parseados del espaciopuerto
        - orbital_facilities: Instalaciones orbitales (boolean)
        - products: Productos disponibles (boolean por código)
        - trade_info: Información comercial (UCN, pasajeros, etc.)
        - bootstrap_data: Datos de bootstrap (tech_level, population, convenio)
        - notes: Notas del usuario
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


def is_valid_starting_planet(planet: Planet) -> Dict[str, Any]:
    """
    Verifica si un planeta es válido para ser planeta inicial.
    
    Requisitos según las reglas del juego:
    - Población > 1000 (population_over_1000 = True)
    - Nivel tecnológico no PR (Primitivo) ni RUD (Rudimentario)
    - Soporte vital no TA (Traje Avanzado) ni TH (Traje Hiperavanzado)
    - Convenio Spacegom = True
    - Al menos un producto disponible para comercio
    
    Args:
        planet: Instancia de Planet a validar
    
    Returns:
        Diccionario con:
        - "is_valid": True si cumple todos los requisitos
        - "checks": Diccionario con resultado de cada validación individual
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


# ===== PLANET CODE ROLL =====

@router.post("/api/games/{game_id}/roll-planet-code")
async def roll_planet_code(
    game_id: str,
    manual_results: Optional[str] = Form(None),
) -> Dict[str, Any]:
    """
    Tira 3d6 para generar un código de planeta y retorna sus datos.
    
    Genera un código de planeta (111-666) mediante tirada de 3d6 y busca
    el planeta correspondiente en la base de datos. También valida si el
    planeta es apto para ser planeta inicial.
    
    Args:
        game_id: Identificador único de la partida
        manual_results: Opcional string con resultados separados por comas (ej: "1,1,1")
        db: Sesión de base de datos SQLAlchemy
    
    Returns:
        Diccionario con:
        - "code": Código del planeta generado (111-666)
        - "dice": Lista de valores de los 3 dados
        - "planet": Datos formateados del planeta o None si no existe
        - "is_valid_start": Resultado de validación para planeta inicial
    
    Raises:
        HTTPException 400: Si los resultados manuales son inválidos
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
    
    # Fetch planet from DynamoDB
    planet = get_planet_by_code(code)

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


# ===== PLANET CRUD =====

@router.get("/api/planets/{code}")
async def get_planet(code: int) -> Dict[str, Any]:
    """Obtener un planeta por su código.

    Devuelve los datos formateados del planeta y la validación para
    determinar si es apto como planeta inicial.
    """
    planet = get_planet_by_code(code)
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {code} not found")
    
    return {
        "planet": format_planet_data(planet),
        "is_valid_start": is_valid_starting_planet(planet)
    }


@router.get("/api/planets")
async def search_planets(name: Optional[str] = None) -> Dict[str, Any]:
    """Buscar planetas por nombre.

    Devuelve una lista de coincidencias (límite 50).
    """
    planets = repo_search_planets(name=name, limit=50)

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


@router.get("/api/planets/next/{current_code}")
async def get_next_planet(current_code: int) -> Dict[str, Any]:
    """
    Obtiene el siguiente planeta en la secuencia 3d6 (búsqueda consecutiva).

    Este endpoint implementa la lógica del manual de juego:
    Si el planeta no es apto para inicio, se busca el siguiente código
    en orden (111 → 112 → 113...) hasta encontrar uno válido.
    """
    next_code = DiceRoller.get_next_planet_code(current_code)
    planet = get_planet_by_code(next_code)

    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {next_code} not found")
        
    return {
        "planet": format_planet_data(planet),
        "is_valid_start": is_valid_starting_planet(planet)
    }


@router.post("/api/planets/{code}/update-notes")
async def update_planet_notes(
    code: int,
    notes: str = Form(...),
) -> Dict[str, Any]:
    """Actualizar notas de un planeta."""
    planet = get_planet_by_code(code)
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {code} not found")

    repo_update_planet_notes(code, notes)
    planet = get_planet_by_code(code)

    return {
        "status": "success",
        "planet": format_planet_data(planet)
    }


@router.post("/api/planets/{code}/update-bootstrap")
async def update_planet_bootstrap(
    code: int,
    tech_level: str = Form(...),
    population_over_1000: bool = Form(...),
) -> Dict[str, Any]:
    """Actualizar datos faltantes del planeta para el proceso de bootstrap.

    Se usa en el flujo de bootstrap cuando faltan datos técnicos del
    planeta y el jugador los proporciona manualmente (`tech_level` y
    `population_over_1000`).
    """
    planet = get_planet_by_code(code)
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {code} not found")

    repo_update_planet_bootstrap(code, tech_level, population_over_1000)

    return {
        "status": "success",
        "planet": {
            "code": code,
            "tech_level": tech_level,
            "population_over_1000": population_over_1000
        }
    }


@router.post("/api/games/{game_id}/set-starting-planet")
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
    row = game.state.get("ship_row")
    col = game.state.get("ship_col")
    if row and col:
        # Convert to 0-based for internal storage
        game.discover_planet(row - 1, col - 1, code)
        game.explore_quadrant(row - 1, col - 1)
        
    game.save()
    return {"status": "success", "code": code}


# ===== NAME SUGGESTIONS API =====

@router.get("/api/suggestions/company-name")
async def suggest_company_name() -> Dict[str, Any]:
    """Retorna un nombre de compañía aleatorio desde el CSV."""
    return {"name": get_random_company_name()}


@router.get("/api/suggestions/ship-name")
async def suggest_ship_name() -> Dict[str, Any]:
    """Retorna un nombre de nave aleatorio desde el CSV."""
    return {"name": get_random_ship_name()}
