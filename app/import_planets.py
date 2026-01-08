"""
Script to import planets from Excel to SQLite database

This script reads the simplified Excel file and populates the database
with proper parsing of spaceport and orbital facilities fields.
"""
import pandas as pd
from app.database import init_db, SessionLocal, Planet


def parse_spaceport(spaceport_str: str) -> dict:
    """
    Parse spaceport code into components
    
    Format: XXX-ZZ-N
    - XXX: Quality (EXC, NOT, MED, BAS, RUD, SIN)
    - ZZ: Fuel density (DB, DM, DA, N)
    - N: Docking price (number)
    
    Args:
        spaceport_str: String like "MED-DB-2"
        
    Returns:
        dict with quality, fuel_density, docking_price
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


def parse_boolean(value, true_values=['X', 'SÍ', 'SI', 'YES', '1', 'TRUE']) -> bool:
    """
    Parse a value to boolean
    
    Args:
        value: Value to parse
        true_values: List of values that should be considered True
        
    Returns:
        Boolean value
    """
    if pd.isna(value):
        return False
    
    return str(value).strip().upper() in true_values


def import_planets_from_excel(excel_path: str):
    """Import planets from simplified Excel file to database"""
    
    # Initialize database
    init_db()
    
    # Read Excel
    df = pd.read_excel(excel_path)
    
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
