"""
Modelos de naves y estadísticas para Spacegom Companion.

Este módulo contiene datos estáticos de todos los modelos de naves disponibles
en Spacegom, incluyendo estadísticas de combate, capacidad y costos según el
manual del juego.

Dependencias: Ninguna (módulo puro de datos)
"""

from typing import Dict, Any

# Diccionario con configuración completa de cada modelo de nave
# Estructura: nombre_modelo: {jump, passengers, storage, damage_support, modifier, cost}
SHIP_MODELS: Dict[str, Dict[str, Any]] = {
    "Basic Starfall": {
        "jump": 1,
        "passengers": 10,
        "storage": 40,
        "damage_support": {"L": 3, "M": 2, "G": 2},
        "modifier": 0,
        "cost": 500
    },
    "Spacegom Fortune": {
        "jump": 1,
        "passengers": 10,
        "storage": 70,
        "damage_support": {"L": 4, "M": 2, "G": 2},
        "modifier": 0,
        "cost": 800
    },
    "Warehouse Ravana": {
        "jump": 1,
        "passengers": 15,
        "storage": 100,
        "damage_support": {"L": 4, "M": 3, "G": 3},
        "modifier": 0,
        "cost": 1200
    },
    "Long Explorer": {
        "jump": 2,
        "passengers": 10,
        "storage": 80,
        "damage_support": {"L": 4, "M": 3, "G": 3},
        "modifier": 1,
        "cost": 1400
    },
    "Space Challenger": {
        "jump": 2,
        "passengers": 15,
        "storage": 100,
        "damage_support": {"L": 4, "M": 4, "G": 3},
        "modifier": 1,
        "cost": 1800
    },
    "High Milkway": {
        "jump": 2,
        "passengers": 25,
        "storage": 150,
        "damage_support": {"L": 4, "M": 4, "G": 4},
        "modifier": 1,
        "cost": 2400
    },
    "Fast Paladin Store": {
        "jump": 2,
        "passengers": 25,
        "storage": 200,
        "damage_support": {"L": 5, "M": 4, "G": 4},
        "modifier": 2,
        "cost": 3000 # Corrected from 300 SC in user text assuming typo given High Milkway cost
    },
    "Tenacity triquadrant": {
        "jump": 3,
        "passengers": 20,
        "storage": 120,
        "damage_support": {"L": 5, "M": 5, "G": 5},
        "modifier": 2,
        "cost": 3300
    },
    "Defiant Navigator": {
        "jump": 3,
        "passengers": 25,
        "storage": 250,
        "damage_support": {"L": 5, "M": 5, "G": 5},
        "modifier": 3,
        "cost": 4000
    },
    "Space Glory": {
        "jump": 4,
        "passengers": 50,
        "storage": 300,
        "damage_support": {"L": 5, "M": 5, "G": 5},
        "modifier": 3,
        "cost": 5000
    }
}

COMPANY_NAME_SUGGESTIONS = [
    "Compañía Starblack",
    "Black Hole LTD",
    "StarKiller & Co",
    "Nebula Traders",
    "Galactic Ventures",
    "Orion Logistics"
]

SHIP_NAME_SUGGESTIONS = [
    "Fénix Dorado",
    "Black Eagle",
    "Halcón Milenario",
    "Estrella Fugaz",
    "Sombra Plateada",
    "Vanguardia Estelar"
]

def get_ship_stats(model_name: str) -> Dict[str, Any]:
    """
    Obtiene las estadísticas de un modelo de nave.
    
    Retorna el diccionario completo con todas las estadísticas del modelo
    especificado. Si el modelo no existe, retorna las estadísticas del
    modelo básico por defecto ("Basic Starfall").
    
    Campos por modelo:
        - jump: Capacidad de salto hiperespacial (rango)
        - passengers: Capacidad máxima de pasajeros
        - storage: Capacidad de almacenamiento en UCN
        - damage_support: Puntos de daño por nivel {"L": leve, "M": moderado, "G": grave}
        - modifier: Modificador general (para cálculos de combate)
        - cost: Costo en Créditos Spacegom (SC)
    
    Args:
        model_name: Nombre del modelo de nave (ej: "Basic Starfall", "Space Glory")
    
    Returns:
        Diccionario con estadísticas del modelo o del modelo básico si no existe
    
    Example:
        >>> stats = get_ship_stats("Basic Starfall")
        >>> stats["storage"]
        40
        >>> stats["cost"]
        500
    """
    return SHIP_MODELS.get(model_name, SHIP_MODELS["Basic Starfall"])
