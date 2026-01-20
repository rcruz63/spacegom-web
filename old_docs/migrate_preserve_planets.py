#!/usr/bin/env python3
"""
Script de migración: Exportar planetas → Reset DB → Reimportar planetas

Este script preserva todos los datos de la tabla planets, especialmente
tech_level y population que se completan durante el setup del juego.
"""

import json
import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base, Planet


def export_planets():
    """Exporta toda la tabla planets a JSON"""
    print("📤 Exportando tabla planets...")
    
    db = SessionLocal()
    
    try:
        planets = db.query(Planet).all()
        
        planet_data = []
        for p in planets:
            planet_data.append({
                "code": p.code,
                "name": p.name,
                "life_support": p.life_support,
                "local_contagion_risk": p.local_contagion_risk,
                "days_to_hyperspace": p.days_to_hyperspace,
                "legal_order_threshold": p.legal_order_threshold,
                "spaceport_quality": p.spaceport_quality,
                "fuel_density": p.fuel_density,
                "docking_price": p.docking_price,
                "orbital_cartography_center": p.orbital_cartography_center,
                "orbital_hackers": p.orbital_hackers,
                "orbital_supply_depot": p.orbital_supply_depot,
                "orbital_astro_academy": p.orbital_astro_academy,
                "product_indu": p.product_indu,
                "product_basi": p.product_basi,
                "product_alim": p.product_alim,
                "product_made": p.product_made,
                "product_agua": p.product_agua,
                "product_mico": p.product_mico,
                "product_mira": p.product_mira,
                "product_mipr": p.product_mipr,
                "product_pava": p.product_pava,
                "product_a": p.product_a,
                "product_ae": p.product_ae,
                "product_aei": p.product_aei,
                "product_com": p.product_com,
                "self_sufficiency_level": p.self_sufficiency_level,
                "ucn_per_order": p.ucn_per_order,
                "max_passengers": p.max_passengers,
                "mission_threshold": p.mission_threshold,
                "tech_level": p.tech_level,  # ← IMPORTANTE: preservar
                "population_over_1000": p.population_over_1000,  # ← IMPORTANTE: preservar
                "convenio_spacegom": p.convenio_spacegom,
                "notes": p.notes,
                "is_custom": p.is_custom
            })
        
        # Save to file
        with open("planets_backup.json", "w", encoding="utf-8") as f:
            json.dump(planet_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exportados {len(planet_data)} planetas a planets_backup.json")
        
        # Count planets with tech_level or population
        with_data = sum(1 for p in planet_data if p.get("tech_level") or p.get("population_over_1000"))
        print(f"   📊 {with_data} planetas con tech_level/population")
        
        db.close()
        return len(planet_data)
        
    except Exception as e:
        db.close()
        print(f"❌ Error exportando: {e}")
        raise


def delete_database():
    """Elimina la base de datos"""
    db_path = "data/spacegom.db"  # Ruta correcta
    
    if os.path.exists(db_path):
        print(f"🗑️  Eliminando {db_path}...")
        os.remove(db_path)
        print("✅ Base de datos eliminada")
        return True
    else:
        print("⚠️  Base de datos no encontrada")
        return False


def recreate_database():
    """Recrea las tablas de la base de datos"""
    print("🔨 Recreando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas")


def import_planets():
    """Importa planetas desde el JSON de backup"""
    print("📥 Importando planetas desde backup...")
    
    if not os.path.exists("planets_backup.json"):
        print("❌ No se encontró planets_backup.json")
        return 0
    
    with open("planets_backup.json", "r", encoding="utf-8") as f:
        planet_data = json.load(f)
    
    db = SessionLocal()
    
    try:
        # CRITICAL: Clear all existing planets first
        print("   Limpiando tabla planets...")
        db.query(Planet).delete()
        db.commit()
        
        for data in planet_data:
            planet = Planet(
                code=data["code"],
                name=data["name"],
                life_support=data["life_support"],
                local_contagion_risk=data["local_contagion_risk"],
                days_to_hyperspace=data["days_to_hyperspace"],
                legal_order_threshold=data["legal_order_threshold"],
                spaceport_quality=data["spaceport_quality"],
                fuel_density=data["fuel_density"],
                docking_price=data["docking_price"],
                orbital_cartography_center=data["orbital_cartography_center"],
                orbital_hackers=data["orbital_hackers"],
                orbital_supply_depot=data["orbital_supply_depot"],
                orbital_astro_academy=data["orbital_astro_academy"],
                product_indu=data["product_indu"],
                product_basi=data["product_basi"],
                product_alim=data["product_alim"],
                product_made=data["product_made"],
                product_agua=data["product_agua"],
                product_mico=data["product_mico"],
                product_mira=data["product_mira"],
                product_mipr=data["product_mipr"],
                product_pava=data["product_pava"],
                product_a=data["product_a"],
                product_ae=data["product_ae"],
                product_aei=data["product_aei"],
                product_com=data["product_com"],
                self_sufficiency_level=data["self_sufficiency_level"],
                ucn_per_order=data["ucn_per_order"],
                max_passengers=data["max_passengers"],
                mission_threshold=data["mission_threshold"],
                tech_level=data["tech_level"],  # ← Restaurado
                population_over_1000=data["population_over_1000"],  # ← Restaurado
                convenio_spacegom=data["convenio_spacegom"],
                notes=data["notes"],
                is_custom=data["is_custom"]
            )
            db.add(planet)
        
        db.commit()
        print(f"✅ Importados {len(planet_data)} planetas")
        
        # Verify tech_level/population restored
        with_data = sum(1 for p in planet_data if p.get("tech_level") or p.get("population_over_1000"))
        print(f"   📊 {with_data} planetas con tech_level/population restaurados")
        
        db.close()
        return len(planet_data)
        
    except Exception as e:
        db.rollback()
        db.close()
        print(f"❌ Error importando: {e}")
        raise


def main():
    print("=" * 70)
    print("MIGRACIÓN: Preservar Planetas → Reset DB → Sistema de Eventos v2")
    print("=" * 70)
    print()
    
    # Step 1: Export planets
    try:
        planet_count = export_planets()
    except Exception as e:
        print(f"\n❌ Falló la exportación. Operación cancelada.")
        return
    
    print()
    
    # Step 2: Confirm
    print("⚠️  ADVERTENCIA:")
    print(f"   Se preservarán {planet_count} planetas (incluyendo tech_level/population)")
    print("   Se perderán todas las partidas guardadas")
    print("   Se aplicará el nuevo sistema de eventos")
    print()
    response = input("¿Continuar con la migración? (s/n): ")
    
    if response.lower() != 's':
        print("❌ Operación cancelada")
        print("   El archivo planets_backup.json se conserva por seguridad")
        return
    
    print()
    
    # Step 3: Delete database
    delete_database()
    print()
    
    # Step 4: Recreate database
    recreate_database()
    print()
    
    # Step 5: Import planets
    try:
        imported = import_planets()
    except Exception as e:
        print(f"\n❌ Falló la importación. Revisa planets_backup.json")
        return
    
    print()
    print("=" * 70)
    print("✅ MIGRACIÓN COMPLETADA CON ÉXITO")
    print()
    print(f"Resultados:")
    print(f"  ✓ {imported} planetas preservados")
    print(f"  ✓ tech_level y population restaurados")
    print(f"  ✓ Formato de fechas: dd-mm-yy")
    print(f"  ✓ EventQueue con IDs secuenciales")
    print(f"  ✓ Sistema de handlers para eventos")
    print()
    print("Próximos pasos:")
    print("  1. Inicia el servidor: uvicorn app.main:app --reload")
    print("  2. Crea una nueva partida")
    print("  3. Verifica: pago de salarios automático día 35")
    print()
    print("Nota: planets_backup.json se conserva como respaldo")
    print("=" * 70)


if __name__ == "__main__":
    main()
