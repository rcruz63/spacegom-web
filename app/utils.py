"""
Utilidades generales para decodificación de códigos del juego y formateo de datos.

Este módulo proporciona funciones para convertir códigos internos del juego
a texto legible para la interfaz de usuario, y utilidades de formateo.

Dependencias: Ninguna (módulo puro de utilidades)
"""

from typing import Dict, Any

# Diccionarios de decodificación - Mapean códigos internos a descripciones legibles

LIFE_SUPPORT_DESCRIPTIONS: Dict[str, str] = {
    "NO": "No es necesario",
    "SO": "Suministro básico de oxígeno",
    "MF": "Máscara con Filtraje",
    "RE": "Respirador",
    "RF": "Respirador con Filtraje",
    "TE": "Traje espacial estándar",
    "TA": "Traje espacial avanzado",
    "TH": "Traje espacial hiperavanzado"
}

TECH_LEVEL_DESCRIPTIONS: Dict[str, str] = {
    "PR": "Primitivo",
    "RUD": "Rudimentario",
    "ES": "Espacial",
    "INT": "Interestelar",
    "POL": "Posinterestelar",
    "N.S": "Nivel superior"
}

SPACEPORT_QUALITY: Dict[str, str] = {
    "EXC": "Excelente",
    "NOT": "Notable",
    "MED": "Medio",
    "BAS": "Básico",
    "RUD": "Rudimentario",
    "SIN": "Sin espaciopuerto"
}

FUEL_DENSITY: Dict[str, str] = {
    "DB": "Densidad Baja",
    "DM": "Densidad Media",
    "DA": "Densidad Alta",
    "N": "Ninguno"
}


def decode_life_support(code: str) -> str:
    """
    Decodifica código de soporte vital a texto legible.
    
    Convierte códigos internos del juego (NO, SO, MF, etc.) a descripciones
    comprensibles para el usuario. Si el código no existe en el diccionario,
    retorna el código original como fallback.
    
    Args:
        code: Código de soporte vital (ej: "NO", "SO", "MF", "RE", "RF", "TE", "TA", "TH")
    
    Returns:
        Descripción legible del código, o el código original si no se encuentra
    
    Example:
        >>> decode_life_support("NO")
        'No es necesario'
        >>> decode_life_support("TE")
        'Traje espacial estándar'
        >>> decode_life_support("UNKNOWN")
        'UNKNOWN'  # Fallback al código original
    """
    return LIFE_SUPPORT_DESCRIPTIONS.get(code, code)


def decode_tech_level(code: str) -> str:
    """
    Decodifica nivel tecnológico a texto legible.
    
    Convierte códigos internos del juego (PR, RUD, ES, etc.) a descripciones
    comprensibles para el usuario. Si el código no existe en el diccionario,
    retorna el código original como fallback.
    
    Args:
        code: Código de nivel tecnológico (ej: "PR", "RUD", "ES", "INT", "POL", "N.S")
    
    Returns:
        Descripción legible del código, o el código original si no se encuentra
    
    Example:
        >>> decode_tech_level("PR")
        'Primitivo'
        >>> decode_tech_level("INT")
        'Interestelar'
    """
    return TECH_LEVEL_DESCRIPTIONS.get(code, code)


def parse_spaceport(spaceport_str: str) -> Dict[str, Any]:
    """
    Parsea string de espaciopuerto en componentes detallados.
    
    El formato del string es "XXX-ZZ-N" donde:
    - XXX: Código de calidad (EXC, NOT, MED, BAS, RUD, SIN)
    - ZZ: Código de densidad de combustible (DB, DM, DA, N)
    - N: Precio de amarre (0-9)
    
    Maneja formatos inválidos gracefully retornando valores por defecto.
    Si el string es "N" o vacío, retorna información de "Sin espaciopuerto".
    
    Args:
        spaceport_str: String de espaciopuerto en formato "XXX-ZZ-N" o "N"
    
    Returns:
        Diccionario con componentes parseados:
        {
            "quality": str,      # Descripción legible de la calidad
            "quality_code": str, # Código original de calidad
            "fuel": str,         # Descripción legible del combustible
            "fuel_code": str,    # Código original de combustible
            "price": int         # Precio de amarre (0-9)
        }
    
    Example:
        >>> parse_spaceport("MED-DB-2")
        {
            "quality": "Medio",
            "quality_code": "MED",
            "fuel": "Densidad Baja",
            "fuel_code": "DB",
            "price": 2
        }
        >>> parse_spaceport("N")
        {
            "quality": "Sin espaciopuerto",
            "quality_code": "SIN",
            "fuel": "Ninguno",
            "fuel_code": "N",
            "price": 0
        }
    
    Note:
        Usado en format_planet_data para mejorar la UX en respuestas API.
        Maneja casos edge en parsing de forma segura.
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
    Formatea fecha del juego en formato "dd-mm-yyyy".
    
    Formatea los componentes de fecha del calendario del juego (35 días/mes,
    12 meses/año) en un string legible con formato estándar.
    
    Args:
        day: Día del mes (1-35)
        month: Mes del año (1-12)
        year: Año del juego
    
    Returns:
        String en formato "dd-mm-yyyy" (ej: "05-03-1" para día 5, mes 3, año 1)
    
    Example:
        >>> format_game_date(5, 3, 1)
        '05-03-1'
        >>> format_game_date(15, 12, 2)
        '15-12-2'
    
    Note:
        Centraliza la lógica de formateo de fechas para mantener consistencia
        en toda la aplicación.
    """
    return f"{day:02d}-{month:02d}-{year}"

