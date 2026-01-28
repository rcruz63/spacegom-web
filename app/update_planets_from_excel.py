"""
Script para actualizar planetas desde archivo Excel SIN eliminar datos existentes.

Este script lee el archivo Excel simplificado y actualiza SOLO los campos que
vienen del Excel, preservando cualquier dato custom o campos que fueron modificados
después de la importación inicial (como tech_level, population_over_1000, notes).

Diferencia con import_planets_from_excel:
    - NO elimina planetas existentes
    - Preserva campos modificados durante el juego
    - Actualiza solo campos que vienen del Excel
    - Crea nuevos planetas si el Excel tiene planetas adicionales

Dependencias:
    - pandas: Lectura de archivos Excel
    - app.database: Modelos y sesión de base de datos
    - app.import_planets: Funciones de parsing reutilizadas
"""

import pandas as pd
from typing import Dict, Any
from app.database import SessionLocal, Planet
from app.import_planets import parse_spaceport, parse_boolean


def update_planets_from_excel(excel_path: str) -> None:
    """
    Actualiza planetas desde archivo Excel preservando datos existentes.
    
    Lee el archivo Excel y actualiza solo los campos que provienen del Excel,
    manteniendo intactos los campos que fueron modificados durante el juego.
    
    Campos actualizados desde Excel:
        - Identificación: name
        - Soporte Vital: life_support, local_contagion_risk, days_to_hyperspace, legal_order_threshold
        - Espaciopuerto: spaceport_quality, fuel_density, docking_price (parsed)
        - Instalaciones Orbitales: orbital_cartography_center, orbital_hackers, etc.
        - Productos: product_indu, product_basi, etc.
        - Comercio: self_sufficiency_level, ucn_per_order, max_passengers, mission_threshold
        - Convenio: convenio_spacegom
    
    Campos preservados (NO se actualizan):
        - tech_level: Nivel tecnológico (seteado en setup)
        - population_over_1000: Población (seteado en setup)
        - notes: Notas del usuario
        - is_custom: Flag de planetas custom
    
    Lógica:
        - Si el planeta existe: actualiza solo campos del Excel
        - Si el planeta no existe: crea nuevo planeta con datos del Excel
    
    Args:
        excel_path: Ruta al archivo Excel con datos de planetas
    
    Raises:
        Exception: Si hay error durante la actualización (hace rollback)
    """
    
    # Read Excel
    df = pd.read_excel(excel_path)
    
    # Normalize column names - strip whitespace and tabs
    df.columns = df.columns.str.strip()
    
    print(f"📖 Leyendo {len(df)} planetas del Excel...")
    print(f"📋 Columnas: {df.columns.tolist()}")
    
    # Create session
    db = SessionLocal()
    
    try:
        updated_count = 0
        created_count = 0
        skipped_count = 0
        
        for idx, row in df.iterrows():
            # Obtener código del planeta
            code = row.get('Code')
            
            # Si el código es NaN, intentar obtenerlo del índice + 111
            if pd.isna(code):
                code = idx + 111
            
            try:
                code = int(code)
            except (ValueError, TypeError):
                print(f" ⚠️ Línea {idx}: código inválido, usando {idx + 111}")
                code = idx + 111
            
            # Check if planet exists
            planet = db.query(Planet).filter(Planet.code == code).first()
            
            # Parse spaceport
            spaceport_data = parse_spaceport(row.get('Espaciopuerto'))
            
            if planet:
                # UPDATE existing planet - only fields from Excel
                planet.name = str(row.get('Nombre', '')).strip()
                
                # Life support and related fields
                planet.life_support = str(row.get('life_support', 'NO')).strip()
                planet.local_contagion_risk = str(row.get('local_contagion_risk', 'NO')).strip()
                planet.days_to_hyperspace = float(row.get('days_to_hyperspace', 0))
                planet.legal_order_threshold = str(row.get('legal_order_threshold', '0')).strip()
                
                # Spaceport (parsed)
                planet.spaceport_quality = spaceport_data['quality']
                planet.fuel_density = spaceport_data['fuel_density']
                planet.docking_price = spaceport_data['docking_price']
                
                # Orbital facilities
                planet.orbital_cartography_center = parse_boolean(row.get('orbital_cartography_center'))
                planet.orbital_hackers = parse_boolean(row.get('orbital_hackers'))
                planet.orbital_supply_depot = parse_boolean(row.get('orbital_supply_depot'))
                planet.orbital_astro_academy = parse_boolean(row.get('orbital_astro_academy'))
                
                # Products
                planet.product_indu = parse_boolean(row.get('INDU'))
                planet.product_basi = parse_boolean(row.get('BASI'))
                planet.product_alim = parse_boolean(row.get('ALIM'))
                planet.product_made = parse_boolean(row.get('MADE'))
                planet.product_agua = parse_boolean(row.get('AGUA'))
                planet.product_mico = parse_boolean(row.get('MICO'))
                planet.product_mira = parse_boolean(row.get('MIRA'))
                planet.product_mipr = parse_boolean(row.get('MIPR'))
                planet.product_pava = parse_boolean(row.get('PAVA'))
                planet.product_a = parse_boolean(row.get('A'))
                planet.product_ae = parse_boolean(row.get('AE'))
                planet.product_aei = parse_boolean(row.get('AEI'))
                planet.product_com = parse_boolean(row.get('COM'))
                
                # Trade information
                planet.self_sufficiency_level = float(row.get('self_sufficiency_level', 0))
                planet.ucn_per_order = float(row.get('ucn_per_order', 0))
                planet.max_passengers = float(row.get('max_passengers', 0))
                planet.mission_threshold = str(row.get('mission_threshold', '0')).strip()
                
                # Update convenio_spacegom from Excel
                planet.convenio_spacegom = parse_boolean(row.get('convenio_spacegom'))
                
                # DO NOT UPDATE: tech_level, population_over_1000, notes, is_custom
                # These are set during game setup or by user customization
                
                updated_count += 1
            else:
                # CREATE new planet (in case Excel has new planets)
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
                    tech_level=None,
                    population_over_1000=None,
                    convenio_spacegom=parse_boolean(row.get('convenio_spacegom')),
                    
                    # Notes and customization
                    notes="",
                    is_custom=False
                )
                
                db.add(planet)
                created_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Actualización completada!")
        print(f"   - Actualizados: {updated_count} planetas")
        print(f"   - Creados: {created_count} planetas")
        print(f"   - Omitidos: {skipped_count} filas")
        
        # Show some examples to verify
        print(f"\n📊 Verificación de planetas actualizados (111-115):")
        sample_planets = db.query(Planet).filter(
            Planet.code >= 111, 
            Planet.code <= 115
        ).all()
        
        for p in sample_planets:
            print(f"   - {p.code}: {p.name}")
            print(f"     life_support: {p.life_support}")
            print(f"     local_contagion_risk: {p.local_contagion_risk}")
            print(f"     convenio_spacegom: {p.convenio_spacegom}")
            print(f"     tech_level: {p.tech_level} (preserved)")
            print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error actualizando planetas: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    excel_path = "data/Base_de_datos_de_planetas_simple.xlsx"
    print("🚀 Iniciando actualización segura de planetas...")
    print("⚠️  Este script NO eliminará datos existentes")
    print("⚠️  Solo actualizará campos que vienen del Excel\n")
    update_planets_from_excel(excel_path)
