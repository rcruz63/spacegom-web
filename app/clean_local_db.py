import sqlite3
import os
import shutil
from pathlib import Path

# Configuración
DB_PATH = 'data/spacegom.db'
GAMES_DIR = 'data/games'

# Tablas que se deben vaciar (NO incluir 'planets')
TABLES_TO_PURGE = [
    'personnel',
    'missions',
    'trade_orders',
    'employee_tasks',
    # Añade aquí cualquier otra tabla dinámica nueva
]

def clean_sqlite():
    print(f"🗄️  Conectando a {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("❌ No se encuentra la base de datos. Nada que limpiar.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n--- INICIANDO PURGA DE SQLITE ---")
    
    for table in TABLES_TO_PURGE:
        try:
            # Verificamos si la tabla existe primero
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            if cursor.fetchone():
                # Borramos todos los registros
                cursor.execute(f"DELETE FROM {table};")
                # Reiniciamos el autoincrement (opcional, por estética)
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
                print(f"✅ Tabla '{table}' vaciada.")
            else:
                print(f"⚠️  Tabla '{table}' no existe (saltando).")
        except Exception as e:
            print(f"❌ Error limpiando tabla {table}: {e}")

    # Confirmar cambios
    conn.commit()
    
    # Optimizar la base de datos para recuperar espacio físico
    cursor.execute("VACUUM;")
    print("🧹 Base de datos optimizada (VACUUM).")
    
    conn.close()
    print("✨ Limpieza de SQLite completada (Planetas intactos).")

def clean_json_files():
    print(f"\n--- LIMPIANDO ARCHIVOS JSON ({GAMES_DIR}) ---")
    
    games_path = Path(GAMES_DIR)
    
    if not games_path.exists():
        print("📂 La carpeta games no existe, creando vacía...")
        games_path.mkdir(parents=True, exist_ok=True)
        return

    # Borrar todo el contenido de data/games
    for item in games_path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
            print(f"🗑️  Borrada carpeta de partida: {item.name}")
        else:
            item.unlink()
            print(f"🗑️  Borrado archivo suelto: {item.name}")
            
    print("✨ Carpeta de partidas vacía.")

if __name__ == "__main__":
    confirm = input("⚠️  ATENCIÓN: Esto borrará TODAS las partidas locales y datos de personal/comercio. \nLos PLANETAS se conservarán. \n¿Proceder? (s/n): ")
    if confirm.lower() == 's':
        clean_sqlite()
        clean_json_files()
    else:
        print("Operación cancelada.")
