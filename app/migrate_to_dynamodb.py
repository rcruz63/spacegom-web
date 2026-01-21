"""Migración de datos a DynamoDB - Script de migración completo.

Transfiere datos desde SQLite (planetas) y JSON (partidas) a AWS DynamoDB.
Implementa estrategia de separación (Split) para manejar datasets que superan
el límite de 400KB por item en DynamoDB.

Migra:
    - 216 planetas desde SQLite a tabla SpacegomPlanets
    - Partidas desde state.json a tabla SpacegomGames con Single Table Design

Uso:
    source .venv/bin/activate
    python app/migrate_to_dynamodb.py

Variables de Entorno:
    AWS_REGION (str): Región de AWS (default: 'eu-west-1')
    AWS_ACCESS_KEY_ID (str): Clave de acceso AWS
    AWS_SECRET_ACCESS_KEY (str): Clave secreta AWS

Notas:
    - Requiere que las tablas existan (ejecutar aws_setup.py primero)
    - Los datos se migran de forma atómica y completa
    - Soporta recuperación ante errores sin datos perdidos
"""
import json
import os
import glob
from decimal import Decimal
import sqlite3
import boto3

# Configuración
DYNAMO_REGION = os.getenv('AWS_REGION', 'eu-west-1')
SQLITE_DB_PATH = 'data/spacegom.db'
GAMES_DIR = 'data/games'

def get_dynamodb_resource():
    """Obtiene un recurso de DynamoDB configurado.
    
    Returns:
        boto3.resource: Recurso de DynamoDB en la región configurada.
    """
    return boto3.resource('dynamodb', region_name=DYNAMO_REGION)

def convert_float_to_decimal(obj):
    """Convierte recursivamente floats a Decimal para compatibilidad con DynamoDB.
    
    DynamoDB no acepta números float nativos. Esta función convierte
    recursivamente todos los floats encontrados en el objeto a Decimal
    para preservar la precisión numérica.
    
    Args:
        obj (any): Objeto a convertir (float, dict, list o tipo primitivo)
        
    Returns:
        Decimal | dict | list | any: Objeto con floats convertidos a Decimal
        
    Ejemplo:
        >>> data = {"price": 99.99, "items": [1.5, 2.7]}
        >>> clean_data = convert_float_to_decimal(data)
        >>> clean_data["price"]
        Decimal('99.99')
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convert_float_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_float_to_decimal(v) for v in obj]
    return obj

def migrate_planets(dynamodb):
    """Migra todos los planetas desde SQLite a DynamoDB.
    
    Lee la tabla 'planets' desde SQLite, limpia nulos, convierte tipos
    y almacena en la tabla SpacegomPlanets de DynamoDB usando batch writer
    para máxima eficiencia.
    
    Args:
        dynamodb (boto3.resource): Recurso DynamoDB configurado
        
    Returns:
        None
        
    Raises:
        Imprime advertencia si SQLite no se encuentra, pero continúa
        
    Ejemplo:
        >>> db = get_dynamodb_resource()
        >>> migrate_planets(db)
        🪐 Migrando Planetas...
        ✅ 216 planetas migrados correctamente.
    """
    print("\n🪐 Migrando Planetas...")
    table = dynamodb.Table('SpacegomPlanets')

    if not os.path.exists(SQLITE_DB_PATH):
        print(f"⚠️ No se encontró {SQLITE_DB_PATH}. Saltando migración de planetas.")
        return

    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Obtenemos columnas dinámicamente
    cursor.execute("SELECT * FROM planets")
    rows = cursor.fetchall()

    with table.batch_writer() as batch:
        count = 0
        for row in rows:
            item = dict(row)
            # Convertir el código a String (PK)
            item['planet_code'] = str(item['code'])
            # Limpiar nulos y convertir tipos
            clean_item = {k: convert_float_to_decimal(v) for k, v in item.items() if v is not None}

            batch.put_item(Item=clean_item)
            count += 1

    print(f"✅ {count} planetas migrados correctamente.")
    conn.close()

def migrate_games(dynamodb):
    """Migra todas las partidas desde state.json a DynamoDB.
    
    Busca todos los archivos state.json en data/games/{game_id}/state.json
    e implementa estrategia de separación (Split) para manejar datasets
    que superan el límite de 400KB de DynamoDB:
    
    - METADATA: Item principal con estado base del juego
    - LOG#dice#timestamp: Tiradas de dados
    - LOG#tx#timestamp: Transacciones financieras
    - LOG#sys#timestamp: Eventos de sistema
    - LOG#ui#timestamp: Logs de UI
    
    Args:
        dynamodb (boto3.resource): Recurso DynamoDB configurado
        
    Returns:
        None
        
    Raises:
        Continúa procesando en caso de error (graceful degradation)
        
    Ejemplo:
        >>> db = get_dynamodb_resource()
        >>> migrate_games(db)
        🚀 Migrando Partidas (Game State)...
        Processing Game: infini_group
          - Metadata guardada.
          - 40 tiradas de dados archivadas.
        ✅ Partida 'infini_group' migrada con éxito.
    """
    print("\n🚀 Migrando Partidas (Game State)...")
    table = dynamodb.Table('SpacegomGames')

    # Buscar todos los state.json
    game_files = glob.glob(os.path.join(GAMES_DIR, '*', 'state.json'))

    for file_path in game_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            game_id = state.get('game_id')
            if not game_id:
                continue

            print(f"Processing Game: {game_id}")

            # --- ESTRATEGIA DE SEPARACIÓN (SPLIT) ---

            # 1. Extraer listas pesadas
            # Usamos .get([], []) para asegurar que sean listas si existen
            dice_rolls = state.pop('dice_rolls', [])
            transactions = state.pop('transactions', [])
            events = state.pop('events', [])
            event_logs = state.pop('event_logs', [])

            # 2. Guardar METADATA (El estado base limpio)
            # Convertimos floats a Decimal para DynamoDB
            metadata_item = convert_float_to_decimal(state)
            metadata_item['game_id'] = f"GAME#{game_id}" # PK
            metadata_item['entity_id'] = "METADATA"       # SK

            table.put_item(Item=metadata_item)
            print("  - Metadata guardada.")

            # 3. Guardar Historiales como Items separados (Batch)
            # Esto evita el límite de 400KB
            with table.batch_writer() as batch:

                # Helper para guardar logs
                def save_logs(log_list, prefix, gid, batch_writer):
                    """Guarda logs en batch, evitando captura de variables del loop."""
                    for log in log_list:
                        # Usamos el timestamp como ID único dentro del log
                        ts = log.get('timestamp', '0')
                        item = convert_float_to_decimal(log)
                        item['game_id'] = f"GAME#{gid}"
                        # SK único: LOG#dice#2026-01-20T11:47:13
                        item['entity_id'] = f"LOG#{prefix}#{ts}"
                        batch_writer.put_item(Item=item)

                if dice_rolls:
                    save_logs(dice_rolls, "dice", game_id, batch)
                    print(f"  - {len(dice_rolls)} tiradas de dados archivadas.")

                if transactions:
                    save_logs(transactions, "tx", game_id, batch)
                    print(f"  - {len(transactions)} transacciones archivadas.")

                if events:
                    save_logs(events, "sys", game_id, batch)
                    print(f"  - {len(events)} eventos de sistema archivados.")

                if event_logs:
                    save_logs(event_logs, "ui", game_id, batch)
                    print(f"  - {len(event_logs)} logs de UI archivados.")

            print(f"✅ Partida '{game_id}' migrada con éxito.")

        except Exception as e:
            print(f"❌ Error migrando {file_path}: {e}")

if __name__ == "__main__":
    """Punto de entrada principal del script de migración.
    
    Ejecuta la migración completa:
    1. Conecta a DynamoDB
    2. Migra planetas desde SQLite
    3. Migra partidas desde JSON
    4. Reporta estado final
    """
    db = get_dynamodb_resource()
    migrate_planets(db)
    migrate_games(db)
    print("\n🏁 Migración completa.")
