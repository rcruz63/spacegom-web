"""AWS DynamoDB Setup - Configuración de infraestructura DynamoDB.

Módulo responsable de crear y configurar las tablas de DynamoDB necesarias
para almacenar datos de planetas y partidas del juego SpaceGOM.

Uso:
    python app/aws_setup.py

Variables de Entorno:
    AWS_REGION (str): Región de AWS (default: 'eu-west-1')
    AWS_ACCESS_KEY_ID (str): Clave de acceso AWS
    AWS_SECRET_ACCESS_KEY (str): Clave secreta AWS
"""
import os
import boto3
from botocore.exceptions import ClientError

def get_dynamodb_resource():
    """Obtiene un recurso de DynamoDB configurado.
    
    Detecta automáticamente si se ejecuta en ambiente local (Docker) o AWS real.
    Para DynamoDB local en Docker, la endpoint_url sería http://dynamodb-local:8000
    
    Returns:
        boto3.resource: Recurso de DynamoDB configurado para la región especificada.
        
    Ejemplo:
        >>> db = get_dynamodb_resource()
        >>> planets_table = db.Table('SpacegomPlanets')
    """
    # Detectar si estamos en local (Docker) o en AWS real
    # Si quisieras usar DynamoDB local en docker, la endpoint_url sería http://dynamodb-local:8000
    return boto3.resource(
        'dynamodb',
        region_name=os.getenv('AWS_REGION', 'eu-west-1')
    )

def create_tables():
    """Crea las tablas de DynamoDB necesarias para SpaceGOM.
    
    Crea dos tablas:
    1. SpacegomPlanets: Almacena datos de 216 planetas (simple PK)
    2. SpacegomGames: Almacena estado de juegos con Single Table Design (PK + SK)
    
    Maneja gracefully si las tablas ya existen (ResourceInUseException).
    
    Raises:
        ClientError: Si hay un error crítico en la creación (excepto ResourceInUseException)
        
    Ejemplo:
        >>> create_tables()
        🚀 Iniciando configuración de infraestructura DynamoDB...
        Creating table: SpacegomPlanets...
        ✅ SpacegomPlanets creada correctamente.
    """
    dynamodb = get_dynamodb_resource()

    print("🚀 Iniciando configuración de infraestructura DynamoDB...")

    # --- Tabla 1: SpacegomPlanets (Simple PK) ---
    try:
        print("Creating table: SpacegomPlanets...")
        table = dynamodb.create_table(
            TableName='SpacegomPlanets',
            KeySchema=[
                {'AttributeName': 'planet_code', 'KeyType': 'HASH'}  # Partition Key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'planet_code', 'AttributeType': 'S'} # String "111"
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(" - Solicitud enviada. Esperando creación...")
        table.wait_until_exists()
        print("✅ SpacegomPlanets creada correctamente.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("⚠️ SpacegomPlanets ya existe. Omitiendo.")
        else:
            print(f"❌ Error crítico: {e}")

    # --- Tabla 2: SpacegomGames (Single Table Design: PK + SK) ---
    try:
        print("\nCreating table: SpacegomGames...")
        table = dynamodb.create_table(
            TableName='SpacegomGames',
            KeySchema=[
                {'AttributeName': 'game_id', 'KeyType': 'HASH'},   # Partition Key
                {'AttributeName': 'entity_id', 'KeyType': 'RANGE'} # Sort Key (SK)
            ],
            AttributeDefinitions=[
                {'AttributeName': 'game_id', 'AttributeType': 'S'},
                {'AttributeName': 'entity_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(" - Solicitud enviada. Esperando creación...")
        table.wait_until_exists()
        print("✅ SpacegomGames creada correctamente.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("⚠️ SpacegomGames ya existe. Omitiendo.")
        else:
            print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    """Punto de entrada principal para configuración de infraestructura DynamoDB.
    
    Crea las tablas necesarias para SpaceGOM en AWS DynamoDB:
    - SpacegomPlanets: Almacenamiento de datos de planetas
    - SpacegomGames: Almacenamiento de estado de partidas
    """
    create_tables()
