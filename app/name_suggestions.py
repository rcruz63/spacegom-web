"""
Utilidades para cargar y servir nombres aleatorios desde archivos CSV.

Proporciona sugerencias para compañías, naves y personal desde archivos CSV
con cache para mejorar el rendimiento.

Archivos CSV utilizados:
    - files/nombres_personal.csv: Nombres de personal (1000 entradas)
    - files/nombres_megacorp.csv: Nombres de compañías (470 entradas)
    - files/nombres_naves.csv: Nombres de naves (500 entradas)

Dependencias:
    - csv: Lectura de archivos CSV
    - random: Selección aleatoria de nombres
    - pathlib: Manejo de rutas de archivos
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
    Carga nombres desde un archivo CSV.
    
    Lee el archivo CSV y extrae los nombres de la segunda columna (formato: ID,Nombre).
    Maneja errores gracefully retornando lista vacía si hay problemas.
    
    Args:
        csv_path: Ruta al archivo CSV a cargar
    
    Returns:
        Lista de nombres extraídos del CSV (lista vacía si hay error o archivo no existe)
    
    Note:
        El formato CSV esperado es: ID,Nombre_X donde la segunda columna contiene el nombre.
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


# Cache de nombres cargados - se inicializa en la primera llamada
_personal_names_cache: List[str] = []
_company_names_cache: List[str] = []
_ship_names_cache: List[str] = []


def get_random_personal_name() -> str:
    """
    Retorna un nombre personal aleatorio con cache.
    
    Carga los nombres desde el CSV en la primera llamada y los cachea
    para llamadas posteriores. Si no hay nombres disponibles, retorna
    un nombre por defecto.
    
    Returns:
        Nombre personal aleatorio del CSV o "John Doe" si hay error
    """
    global _personal_names_cache
    
    if not _personal_names_cache:
        _personal_names_cache = load_names_from_csv(NOMBRES_PERSONAL_CSV)
    
    if not _personal_names_cache:
        return "John Doe"
    
    return random.choice(_personal_names_cache)


def get_random_company_name() -> str:
    """
    Retorna un nombre de compañía aleatorio con cache.
    
    Carga los nombres desde el CSV en la primera llamada y los cachea
    para llamadas posteriores. Si no hay nombres disponibles, retorna
    un nombre por defecto.
    
    Returns:
        Nombre de compañía aleatorio del CSV o "Stellar Corporation" si hay error
    """
    global _company_names_cache
    
    if not _company_names_cache:
        _company_names_cache = load_names_from_csv(NOMBRES_MEGACORP_CSV)
    
    if not _company_names_cache:
        return "Stellar Corporation"
    
    return random.choice(_company_names_cache)


def get_random_ship_name() -> str:
    """
    Retorna un nombre de nave aleatorio con cache.
    
    Carga los nombres desde el CSV en la primera llamada y los cachea
    para llamadas posteriores. Si no hay nombres disponibles, retorna
    un nombre por defecto.
    
    Returns:
        Nombre de nave aleatorio del CSV o "Enterprise" si hay error
    """
    global _ship_names_cache
    
    if not _ship_names_cache:
        _ship_names_cache = load_names_from_csv(NOMBRES_NAVES_CSV)
    
    if not _ship_names_cache:
        return "Enterprise"
    
    return random.choice(_ship_names_cache)


def reload_names() -> None:
    """
    Recarga todos los nombres desde los archivos CSV.
    
    Útil si los archivos CSV se modifican durante la ejecución y se
    necesita refrescar el cache. Limpia los caches existentes y vuelve
    a cargar desde los archivos.
    """
    global _personal_names_cache, _company_names_cache, _ship_names_cache
    
    _personal_names_cache = load_names_from_csv(NOMBRES_PERSONAL_CSV)
    _company_names_cache = load_names_from_csv(NOMBRES_MEGACORP_CSV)
    _ship_names_cache = load_names_from_csv(NOMBRES_NAVES_CSV)
