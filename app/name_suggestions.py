"""
Utilidades para cargar y servir nombres desde archivos CSV
"""
import csv
import random
from pathlib import Path
from typing import List

# Rutas a los archivos CSV
FILES_DIR = Path(__file__).parent.parent / "files"
NOMBRES_PERSONAL_CSV = FILES_DIR / "nombres_personal.csv"
NOMBRES_MEGACORP_CSV = FILES_DIR / "nombres_megacorp.csv"
NOMBRES_NAVES_CSV = FILES_DIR / "nombres_naves.csv"


def load_names_from_csv(csv_path: Path) -> List[str]:
    """
    Carga nombres desde un archivo CSV
    
    Args:
        csv_path: Ruta al archivo CSV
        
    Returns:
        Lista de nombres
    """
    names = []
    
    if not csv_path.exists():
        return names
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Obtener el valor de la segunda columna (índice 1)
                # Los CSV tienen formato: ID,Nombre_X
                name = list(row.values())[1] if len(row.values()) > 1 else None
                if name:
                    names.append(name.strip())
    except Exception as e:
        print(f"Error loading CSV {csv_path}: {e}")
    
    return names


# Cache de nombres cargados
_personal_names_cache: List[str] = []
_company_names_cache: List[str] = []
_ship_names_cache: List[str] = []


def get_random_personal_name() -> str:
    """
    Retorna un nombre personal aleatorio
    """
    global _personal_names_cache
    
    if not _personal_names_cache:
        _personal_names_cache = load_names_from_csv(NOMBRES_PERSONAL_CSV)
    
    if not _personal_names_cache:
        return "John Doe"
    
    return random.choice(_personal_names_cache)


def get_random_company_name() -> str:
    """
    Retorna un nombre de compañía aleatorio
    """
    global _company_names_cache
    
    if not _company_names_cache:
        _company_names_cache = load_names_from_csv(NOMBRES_MEGACORP_CSV)
    
    if not _company_names_cache:
        return "Stellar Corporation"
    
    return random.choice(_company_names_cache)


def get_random_ship_name() -> str:
    """
    Retorna un nombre de nave aleatorio
    """
    global _ship_names_cache
    
    if not _ship_names_cache:
        _ship_names_cache = load_names_from_csv(NOMBRES_NAVES_CSV)
    
    if not _ship_names_cache:
        return "Enterprise"
    
    return random.choice(_ship_names_cache)


def reload_names():
    """
    Recarga todos los nombres desde los archivos CSV
    Útil si los archivos se modifican en runtime
    """
    global _personal_names_cache, _company_names_cache, _ship_names_cache
    
    _personal_names_cache = load_names_from_csv(NOMBRES_PERSONAL_CSV)
    _company_names_cache = load_names_from_csv(NOMBRES_MEGACORP_CSV)
    _ship_names_cache = load_names_from_csv(NOMBRES_NAVES_CSV)
