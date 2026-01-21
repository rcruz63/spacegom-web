# Migrate to DynamoDB - Script de Migración de Datos

## Descripción General

Script de migración completo que transfiere datos desde SQLite y JSON a AWS DynamoDB. Gestiona la conversión de tipos, optimización de almacenamiento y manejo de datasets grandes que superan el límite de 400KB de DynamoDB.

**Ubicación**: `app/migrate_to_dynamodb.py`  
**Tipo**: Herramienta de migración  
**Estado**: Fase 2 - Migración de Datos  
**Versión**: 1.0.0  

## Dependencias

- **boto3** >= 1.42.30: Cliente SDK de AWS
- **botocore** >= 1.42.30: Cliente de bajo nivel
- **sqlite3**: Módulo estándar para lectura de base de datos SQLite
- **json**: Módulo estándar para lectura de JSON
- **pathlib**, **glob**, **os**: Módulos estándar para gestión de archivos
- **decimal**: Módulo estándar para conversión de tipos

```python
import sqlite3
import json
import os
import glob
from pathlib import Path
from decimal import Decimal
import boto3
```

## Configuración

```python
DYNAMO_REGION = os.getenv('AWS_REGION', 'eu-west-1')  # Región de AWS
SQLITE_DB_PATH = 'data/spacegom.db'                   # Ruta a base de datos SQLite
GAMES_DIR = 'data/games'                              # Directorio de partidas JSON
```

## Funciones Principales

### `get_dynamodb_resource()`

Obtiene un recurso de DynamoDB desde la región especificada.

**Parámetros**: Ninguno

**Retorna**: 
- `boto3.resource`: Recurso DynamoDB

**Ejemplo**:
```python
db = get_dynamodb_resource()
```

---

### `convert_float_to_decimal(obj)`

Convierte recursivamente floats a Decimal para compatibilidad con DynamoDB.

**Parámetros**:
- `obj` (any): Objeto a convertir (puede ser float, dict, list, o tipo primitivo)

**Retorna**:
- `Decimal | dict | list | any`: Objeto con floats convertidos a Decimal

**Por qué es necesario**:
DynamoDB no acepta números float nativos. Requiere convertirlos a Decimal para evitar pérdidas de precisión.

**Ejemplo**:
```python
data = {"price": 99.99, "items": [1.5, 2.7]}
clean_data = convert_float_to_decimal(data)
# {"price": Decimal('99.99'), "items": [Decimal('1.5'), Decimal('2.7')]}
```

---

### `migrate_planets(dynamodb)`

Migra todos los datos de planetas desde SQLite a la tabla `SpacegomPlanets` de DynamoDB.

**Parámetros**:
- `dynamodb` (boto3.resource): Recurso DynamoDB

**Retorna**: None

**Proceso**:
1. Valida que el archivo `data/spacegom.db` exista
2. Lee la tabla `planets` desde SQLite
3. Convierte códigos planetarios a strings (PK)
4. Limpia valores nulos
5. Convierte floats a Decimal
6. Usa batch_writer para inserción eficiente

**Ejemplo de salida**:
```
🪐 Migrando Planetas...
✅ 216 planetas migrados correctamente.
```

---

### `migrate_games(dynamodb)`

Migra todas las partidas desde archivos `state.json` a la tabla `SpacegomGames` usando Single Table Design.

**Parámetros**:
- `dynamodb` (boto3.resource): Recurso DynamoDB

**Retorna**: None

**Estrategia de Separación (Split)**:

Para evitar exceder el límite de 400KB por item en DynamoDB:

1. **Metadata Item** (`entity_id: METADATA`)
   - Estado base limpio del juego
   - Información principal de la partida
   - Contiene: game_id, ship_name, company_name, treasury, etc.

2. **Historiales Separados** (múltiples items)
   - `LOG#dice#timestamp`: Tiradas de dados
   - `LOG#tx#timestamp`: Transacciones financieras
   - `LOG#sys#timestamp`: Eventos de sistema
   - `LOG#ui#timestamp`: Logs de UI para el usuario

**Ejemplo de estructura**:
```json
{
  "game_id": "GAME#infini_group",
  "entity_id": "METADATA",
  "company_name": "Infini Group",
  "ship_name": "North Star",
  "treasury": 416,
  "created_at": "2026-01-20T11:47:09.776196"
}

{
  "game_id": "GAME#infini_group",
  "entity_id": "LOG#dice#2026-01-20T11:47:13.889465",
  "num_dice": 2,
  "results": [2, 1],
  "total": 3
}
```

**Ventajas**:
- Evita límite de 400KB
- Permite queries por tipo de log
- Facilita archivado y purga de historiales antiguos
- Escalable para partidas muy largas

**Salida de ejemplo**:
```
🚀 Migrando Partidas (Game State)...
Processing Game: infini_group
  - Metadata guardada.
  - 40 tiradas de dados archivadas.
  - 2 transacciones archivadas.
  - 14 eventos de sistema archivados.
  - 13 logs de UI archivados.
✅ Partida 'infini_group' migrada con éxito.
```

## Mapeo de Datos

### Planetas (SpacegomPlanets)

```
SQLite: planets.code (integer) → DynamoDB: planet_code (String)
SQLite: planets.* → DynamoDB: item.*
```

**Limpieza**:
- Se descartan todos los campos con valor `NULL`
- Se convierten floats a Decimal

---

### Partidas (SpacegomGames - Single Table Design)

```
game_id: Partition Key
entity_id: Sort Key

Patrones de entity_id:
- METADATA: Estado principal del juego
- LOG#dice#{timestamp}: Tirada de dados
- LOG#tx#{timestamp}: Transacción
- LOG#sys#{timestamp}: Evento de sistema
- LOG#ui#{timestamp}: Log de UI
```

## Manejo de Errores

```python
except Exception as e:
    print(f"❌ Error migrando {file_path}: {e}")
```

**Errores comunes**:
- Archivo SQLite no encontrado: Salta migración de planetas
- JSON inválido: Registra error y continúa con siguiente partida
- Conexión a DynamoDB: Se propaga el error (revisar credenciales AWS)
- Tamaño de item > 400KB: Item se rechaza (mitigado con estrategia Split)

## Variables de Entorno Requeridas

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `AWS_REGION` | `eu-west-1` | Región de DynamoDB |
| `AWS_ACCESS_KEY_ID` | - | Credencial AWS (requerida) |
| `AWS_SECRET_ACCESS_KEY` | - | Credencial AWS (requerida) |

## Uso

### Migración Completa

```bash
# Activar entorno virtual
source .venv/bin/activate

# Configurar credenciales (una sola vez)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=eu-west-1

# Ejecutar migración
python app/migrate_to_dynamodb.py
```

### Con DynamoDB Local (Docker)

```bash
# En docker-compose.yml, asegurar que dynamodb-local esté corriendo
docker-compose up dynamodb-local

# Ejecutar con endpoint local
export AWS_REGION=us-east-1  # DynamoDB local usa esta región
export AWS_ENDPOINT_URL=http://localhost:8000
python app/migrate_to_dynamodb.py
```

## Diseño de Partición (Partition Design)

### Single Table Design - SpacegomGames

**Ventajas**:

1. **Queries Eficientes**:
   ```
   # Obtener todo de un juego
   query(KeyConditionExpression="game_id = :gid", ExpressionAttributeValues={":gid": "GAME#infini_group"})
   
   # Obtener solo transacciones
   query(KeyConditionExpression="game_id = :gid AND begins_with(entity_id, :sk)", 
         ExpressionAttributeValues={":gid": "GAME#infini_group", ":sk": "LOG#tx"})
   ```

2. **Escalabilidad**: Evita hotspots de lectura/escritura

3. **Costo**: Una sola tabla vs múltiples tablas

4. **Transacciones**: Posibilidad de transacciones ACID entre items del mismo juego

## Consideraciones de Performance

### Batch Writer
- Agrupa hasta 25 items por solicitud
- Reduce latencia de red
- Maneja reintentos automáticamente
- Ideal para migraciones en lote

### Conversión de Tipos
- Float → Decimal: Necesario para DynamoDB
- Recursive para nested objects
- Preserva precisión numérica

### Límites de DynamoDB
- **Max item size**: 400 KB (mitigado con Split strategy)
- **Max batch size**: 16 MB (respetado automáticamente)
- **Throughput**: Configurado en 5 RCU / 5 WCU por tabla

## Monitoreo de Migración

**Métricas a verificar**:
```bash
# Contar items en tabla de planetas
aws dynamodb scan --table-name SpacegomPlanets --select COUNT_ITEMS

# Contar items en tabla de juegos
aws dynamodb scan --table-name SpacegomGames --select COUNT_ITEMS

# Obtener una partida específica
aws dynamodb query --table-name SpacegomGames \
  --key-condition-expression "game_id = :gid" \
  --expression-attribute-values '{":gid": {"S": "GAME#infini_group"}}'
```

## Rollback

Si hay problemas, las tablas pueden borrarse y recrearse:

```python
# En AWS CLI
aws dynamodb delete-table --table-name SpacegomPlanets
aws dynamodb delete-table --table-name SpacegomGames

# Luego ejecutar aws_setup.py nuevamente para recrear
python app/aws_setup.py
```

## Próximas Fases

### Fase 3: Sincronización Bidireccional
- Mantener SQLite y DynamoDB en sync
- Implementar listeners para cambios
- Fallback a SQLite si DynamoDB no disponible

### Fase 4: Optimizaciones
- Implementar Global Secondary Indexes (GSI)
- Agregar TTL para datos temporales
- Archivado automático de historiales antiguos

### Fase 5: Backup y Recuperación
- Backups automáticos a S3
- Point-in-time recovery
- Snapshots periódicos

## Logs de Ejecución Típicos

```
🪐 Migrando Planetas...
✅ 216 planetas migrados correctamente.

🚀 Migrando Partidas (Game State)...
Processing Game: infini_group
  - Metadata guardada.
  - 40 tiradas de dados archivadas.
  - 2 transacciones archivadas.
  - 14 eventos de sistema archivados.
  - 13 logs de UI archivados.
✅ Partida 'infini_group' migrada con éxito.

Processing Game: rival_corp
  - Metadata guardada.
  - 8 tiradas de dados archivadas.
  - 0 transacciones archivadas.
  - 3 eventos de sistema archivados.
  - 3 logs de UI archivados.
✅ Partida 'rival_corp' migrada con éxito.

🏁 Migración completa.
```

## Referencias

- [AWS DynamoDB Item Size Limits](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html)
- [DynamoDB Single Table Design](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Boto3 Batch Operations](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/table/batch_writer.html)
- [Python Decimal Module](https://docs.python.org/3/library/decimal.html)