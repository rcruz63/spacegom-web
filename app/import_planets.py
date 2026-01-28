"""
Script para importar planetas desde archivo Excel simplificado a la base de datos SQLite.

Este script lee el archivo Excel y pobla la base de datos con parsing adecuado
de campos complejos como espaciopuerto e instalaciones orbitales.

Proceso:
    1. Inicializa la base de datos
    2. Lee archivo Excel con pandas
    3. Limpia nombres de columnas
    4. Elimina planetas existentes (no custom)
    5. Para cada fila: parsea código, espaciopuerto y crea objeto Planet
    6. Commit y muestra estadísticas

Dependencias:
    - pandas: Lectura de archivos Excel
    - app.database: Modelos y sesión de base de datos
"""

import pandas as pd
from typing import Dict, Any
from app.database import init_db, SessionLocal, Planet


def parse_spaceport(spaceport_str: str) -> Dict[str, Any]:
    """
    Parsea código de espaciopuerto en componentes.
    
    El formato del código es "XXX-ZZ-N" donde:
    - XXX: Calidad del espaciopuerto (EXC, NOT, MED, BAS, RUD, SIN)
    - ZZ: Densidad de combustible (DB, DM, DA, N)
    - N: Precio de amarre (número 0-9)
    
    Maneja valores NaN y formatos inválidos retornando valores por defecto.
    
    Args:
        spaceport_str: String con código de espaciopuerto (ej: "MED-DB-2")
        
    Returns:
        Diccionario con:
        {
            "quality": str,        # Código de calidad
            "fuel_density": str,    # Código de densidad de combustible
            "docking_price": int    # Precio de amarre
        }
        
    Note:
        Si el string es NaN o tiene formato inválido, retorna valores por defecto
        (SIN, N, 0).
    """
    if pd.isna(spaceport_str) or not spaceport_str:
        return {
            "quality": "SIN",
            "fuel_density": "N",
            "docking_price": 0
        }
    
    parts = str(spaceport_str).strip().split('-')
    
    if len(parts) != 3:
        # Handle edge cases
        return {
            "quality": "SIN",
            "fuel_density": "N",
            "docking_price": 0
        }
    
    quality = parts[0].strip()
    fuel_density = parts[1].strip()
    
    try:
        docking_price = int(parts[2].strip())
    except (ValueError, IndexError):
        docking_price = 0
    
    return {
        "quality": quality,
        "fuel_density": fuel_density,
        "docking_price": docking_price
    }


def parse_boolean(value: Any, true_values: list = None) -> bool:
    """
    Convierte valor a booleano con lista configurable de valores verdaderos.
    
    Útil para parsear campos del Excel que pueden venir en diferentes formatos
    (X, SÍ, SI, YES, 1, TRUE, etc.). Si el valor no está en la lista de valores
    verdaderos o es NaN, retorna False.
    
    Args:
        value: Valor a convertir (puede ser string, número, NaN, etc.)
        true_values: Lista de valores que se consideran True (default: ['X', 'SÍ', 'SI', 'YES', '1', 'TRUE'])
        
    Returns:
        True si el valor está en la lista de valores verdaderos, False en caso contrario
    """
    if true_values is None:
        true_values = ['X', 'SÍ', 'SI', 'YES', '1', 'TRUE']
    if pd.isna(value):
        return False
    
    return str(value).strip().upper() in true_values


def import_planets_from_excel(excel_path: str) -> None:
    """
    Importa planetas desde archivo Excel a la base de datos.
    
    Lee el archivo Excel, parsea cada fila y crea objetos Planet en la base de datos.
    Elimina planetas existentes que no sean custom antes de importar.
    
    Campos mapeados desde Excel:
        - Identificación: code, name
        - Soporte Vital: life_support, local_contagion_risk, days_to_hyperspace, legal_order_threshold
        - Espaciopuerto: spaceport_quality, fuel_density, docking_price (parsed desde string)
        - Instalaciones Orbitales: orbital_cartography_center, orbital_hackers, etc. (boolean)
        - Productos: product_indu, product_basi, etc. (boolean)
        - Comercio: self_sufficiency_level, ucn_per_order, max_passengers, mission_threshold
        - Validación: convenio_spacegom (tech_level y population_over_1000 se llenan después)
    
    Campos preservados/por defecto:
        - tech_level: None (se llena durante setup)
        - population_over_1000: None (se llena durante setup)
        - notes: "" (vacío)
        - is_custom: False (no son planetas custom)
    
    Args:
        excel_path: Ruta al archivo Excel con datos de planetas
    
    Raises:
        Exception: Si hay error durante la importación (hace rollback)
    """
    
    # Initialize database
    init_db()
    
    # Read Excel
    df = pd.read_excel(excel_path)
    
    # Normalize column names - strip whitespace and tabs
    df.columns = df.columns.str.strip()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Clear existing planets (only non-custom ones)
        db.query(Planet).filter(Planet.is_custom == False).delete()
        
        imported_count = 0
        skipped_count = 0
        
        # El nuevo Excel tiene columnas con nombres claros
        for idx, row in df.iterrows():
            # Obtener código del planeta
            code = row.get('Code')
            
            # Si el código es NaN, intentar obtenerlo del índice + 111
            if pd.isna(code):
                # Los códigos empiezan en 111 y siguen la secuencia 3d6
                # Podemos asumir que el Excel está ordenado
                code = idx + 111
            
            try:
                code = int(code)
            except (ValueError, TypeError):
                print(f" ⚠️ Línea {idx}: código inválido, usando {idx + 111}")
                code = idx + 111
            
            # Parse spaceport
            spaceport_data = parse_spaceport(row.get('Espaciopuerto'))
            
            # Create planet object
            planet = Planet(
                code=code,
                name=str(row.get('Nombre', '')).strip(),
                
                # Life support
                life_support=str(row.get('life_support', 'NO')).strip(),
                local_contagion_risk=str(row.get('local_contagion_risk', 'NO')).strip(),
                days_to_hyperspace=float(row.get('days_to_hyperspace', 0)),
                legal_order_threshold=str(row.get('legal_order_threshold', '0')).strip(),
                
                # Spaceport (parsed)
                spaceport_quality=spaceport_data['quality'],
                fuel_density=spaceport_data['fuel_density'],
                docking_price=spaceport_data['docking_price'],
                
                # Orbital facilities
                orbital_cartography_center=parse_boolean(row.get('orbital_cartography_center')),
                orbital_hackers=parse_boolean(row.get('orbital_hackers')),
                orbital_supply_depot=parse_boolean(row.get('orbital_supply_depot')),
                orbital_astro_academy=parse_boolean(row.get('orbital_astro_academy')),
                
                # Products
                product_indu=parse_boolean(row.get('INDU')),
                product_basi=parse_boolean(row.get('BASI')),
                product_alim=parse_boolean(row.get('ALIM')),
                product_made=parse_boolean(row.get('MADE')),
                product_agua=parse_boolean(row.get('AGUA')),
                product_mico=parse_boolean(row.get('MICO')),
                product_mira=parse_boolean(row.get('MIRA')),
                product_mipr=parse_boolean(row.get('MIPR')),
                product_pava=parse_boolean(row.get('PAVA')),
                product_a=parse_boolean(row.get('A')),
                product_ae=parse_boolean(row.get('AE')),
                product_aei=parse_boolean(row.get('AEI')),
                product_com=parse_boolean(row.get('COM')),
                
                # Trade information
                self_sufficiency_level=float(row.get('self_sufficiency_level', 0)),
                ucn_per_order=float(row.get('ucn_per_order', 0)),
                max_passengers=float(row.get('max_passengers', 0)),
                mission_threshold=str(row.get('mission_threshold', '0')).strip(),
                
                # Validation for starting planet
                tech_level=None,  # To be filled during setup
                population_over_1000=None,  # To be filled during setup
                convenio_spacegom=parse_boolean(row.get('convenio_spacegom')),
                
                # Notes and customization
                notes="",
                is_custom=False
            )
            
            # Add to database
            db.add(planet)
            imported_count += 1
        
       # Commit all changes
        db.commit()
        
        print(f"✅ Importación completada!")
        print(f"   - Importados: {imported_count} planetas")
        print(f"   - Omitidos: {skipped_count} filas")
        
        # Show some examples
        print(f"\n📊 Muestra de planetas:")
        sample_planets = db.query(Planet).limit(5).all()
        for p in sample_planets:
            print(f"   - {p.code}: {p.name} ({p.spaceport_quality}-{p.fuel_density}-{p.docking_price})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error importando planetas: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    excel_path = "data/Base_de_datos_de_planetas_simple.xlsx"
    import_planets_from_excel(excel_path)
