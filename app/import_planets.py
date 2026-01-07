"""
Script to import planets from Excel to SQLite database
"""
import pandas as pd
from database import init_db, SessionLocal, Planet


def import_planets_from_excel(excel_path: str):
    """Import planets from Excel file to database"""
    
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
        
        for idx, row in df.iterrows():
            # Skip header row (row 0)
            if idx == 0:
                continue
            
            # Get planet code from *1 column
            code = row.get('*1')
            
            # Skip if no code
            if pd.isna(code):
                skipped_count += 1
                continue
            
            try:
                code = int(code)
            except (ValueError, TypeError):
                skipped_count += 1
                continue
            
            # Create planet object
            planet = Planet(
                code=code,
                name=row.get('Nombre', ''),
                life_support_1=str(row.get('*2', '')).strip() if not pd.isna(row.get('*2')) else None,
                life_support_2=str(row.get('*3', '')).strip() if not pd.isna(row.get('*3')) else None,
                life_support_3=str(row.get('*4', '')).strip() if not pd.isna(row.get('*4')) else None,
                life_support_4=str(row.get('*5', '')).strip() if not pd.isna(row.get('*5')) else None,
                life_support_5=str(row.get('*6', '')).strip() if not pd.isna(row.get('*6')) else None,
                spaceport=str(row.get('Espaciopuerto', '')).strip() if not pd.isna(row.get('Espaciopuerto')) else None,
                orbital_facilities=str(row.get('Instalaciones orbitales', '')).strip() if not pd.isna(row.get('Instalaciones orbitales')) else None,
                # Products
                product_indu=str(row.get('Unnamed: 13', '')).strip().upper() == 'X',
                product_basi=str(row.get('Unnamed: 14', '')).strip().upper() == 'X',
                product_alim=str(row.get('Unnamed: 15', '')).strip().upper() == 'X',
                product_made=str(row.get('Unnamed: 16', '')).strip().upper() == 'X',
                product_agua=str(row.get('Unnamed: 17', '')).strip().upper() == 'X',
                product_mico=str(row.get('Unnamed: 18', '')).strip().upper() == 'X',
                product_mira=str(row.get('Unnamed: 19', '')).strip().upper() == 'X',
                product_mipr=str(row.get('Unnamed: 20', '')).strip().upper() == 'X',
                product_pava=str(row.get('Unnamed: 21', '')).strip().upper() == 'X',
                product_a=str(row.get('Unnamed: 22', '')).strip().upper() == 'X',
                product_ae=str(row.get('Unnamed: 23', '')).strip().upper() == 'X',
                product_aei=str(row.get('Unnamed: 24', '')).strip().upper() == 'X',
                product_com=str(row.get('Unnamed: 25', '')).strip().upper() == 'X' if 'Unnamed: 25' in row else False,
                # Additional fields
                field_7=str(row.get('*7', '')).strip() if not pd.isna(row.get('*7')) else None,
                field_8=str(row.get('*8', '')).strip() if not pd.isna(row.get('*8')) else None,
                field_9=str(row.get('*9', '')).strip() if not pd.isna(row.get('*9')) else None,
                field_10=str(row.get('*10', '')).strip() if not pd.isna(row.get('*10')) else None,
                is_custom=False
            )
            
            # Add to database
            db.add(planet)
            imported_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"✅ Importation complete!")
        print(f"   - Imported: {imported_count} planets")
        print(f"   - Skipped: {skipped_count} rows")
        
        # Show some examples
        print(f"\n📊 Sample planets:")
        sample_planets = db.query(Planet).limit(5).all()
        for p in sample_planets:
            print(f"   - {p.code}: {p.name} ({p.spaceport})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error importing planets: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    excel_path = "data/Base_de_datos_de_planetas.xlsx"
    import_planets_from_excel(excel_path)
