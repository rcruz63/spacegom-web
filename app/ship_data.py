"""
Ship model data and utility functions for Spacegom Companion
"""

SHIP_MODELS = {
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

def get_ship_stats(model_name: str) -> dict:
    return SHIP_MODELS.get(model_name, SHIP_MODELS["Basic Starfall"])
