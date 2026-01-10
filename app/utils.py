"""
Utility functions for Spacegom
"""

# Diccionarios de decodificación
LIFE_SUPPORT_DESCRIPTIONS = {
    "NO": "No es necesario",
    "SO": "Suministro básico de oxígeno",
    "MF": "Máscara con Filtraje",
    "RE": "Respirador",
    "RF": "Respirador con Filtraje",
    "TE": "Traje espacial estándar",
    "TA": "Traje espacial avanzado",
    "TH": "Traje espacial hiperavanzado"
}

TECH_LEVEL_DESCRIPTIONS = {
    "PR": "Primitivo",
    "RUD": "Rudimentario",
    "ES": "Estándar",
    "INT": "Intermedio",
    "POL": "Pólvora",
    "N.S": "No Significativo"
}

SPACEPORT_QUALITY = {
    "EXC": "Excelente",
    "NOT": "Notable",
    "MED": "Medio",
    "BAS": "Básico",
    "RUD": "Rudimentario",
    "SIN": "Sin espaciopuerto"
}

FUEL_DENSITY = {
    "DB": "Densidad Baja",
    "DM": "Densidad Media",
    "DA": "Densidad Alta",
    "N": "Ninguno"
}


def decode_life_support(code: str) -> str:
    """Decodifica código de soporte vital a texto legible"""
    return LIFE_SUPPORT_DESCRIPTIONS.get(code, code)


def decode_tech_level(code: str) -> str:
    """Decodifica nivel tecnológico a texto legible"""
    return TECH_LEVEL_DESCRIPTIONS.get(code, code)


def parse_spaceport(spaceport_str: str) -> dict:
    """
    Parsea string de espaciopuerto (formato: XXX-ZZ-N) en componentes
    
    Ejemplo: "MED-DB-2" -> {
        "quality": "Medio",
        "quality_code": "MED",
        "fuel": "Densidad Baja",
        "fuel_code": "DB",
        "price": 2
    }
    """
    if not spaceport_str or spaceport_str == "N":
        return {
            "quality": "Sin espaciopuerto",
            "quality_code": "SIN",
            "fuel": "Ninguno",
            "fuel_code": "N",
            "price": 0
        }
    
    parts = spaceport_str.split('-')
    if len(parts) != 3:
        return {
            "quality": spaceport_str,
            "quality_code": spaceport_str,
            "fuel": "Desconocido",
            "fuel_code": "N",
            "price": 0
        }
    
    quality_code, fuel_code, price = parts
    
    return {
        "quality": SPACEPORT_QUALITY.get(quality_code, quality_code),
        "quality_code": quality_code,
        "fuel": FUEL_DENSITY.get(fuel_code, fuel_code),
        "fuel_code": fuel_code,
        "price": int(price)
    }


def format_game_date(day: int, month: int, year: int) -> str:
    """
    Formatea fecha del juego en formato dd-mm-yyyy
    
    Args:
        day: Día (1-35)
        month: Mes (1-12)
        year: Año
        
    Returns:
        String en formato dd-mm-yyyy
    """
    return f"{day:02d}-{month:02d}-{year}"

