# AWS Setup - Configuración de Infraestructura DynamoDB

## Descripción General

Módulo de configuración de la infraestructura de AWS DynamoDB para el proyecto SpaceGOM. Proporciona funciones para crear y gestionar tablas de DynamoDB necesarias para almacenar datos de planetas y juegos.

**Ubicación**: `app/aws_setup.py`  
**Estado**: En desarrollo  
**Versión**: 1.0.0  

## Dependencias

- **boto3** >= 1.42.30: Cliente SDK de AWS para Python
- **botocore** >= 1.42.30: Cliente de bajo nivel para AWS

```python
import os
import sys
import boto3
from botocore.exceptions import ClientError
```

## Funciones Principales

### `get_dynamodb_resource()`

Obtiene un recurso de DynamoDB, detectando automáticamente si se ejecuta en ambiente local (Docker) o en AWS real.

**Parámetros**: Ninguno

**Retorna**: 
- `boto3.resource`: Recurso de DynamoDB configurado con la región especificada en la variable de entorno `AWS_REGION` o `eu-west-1` por defecto.

**Ejemplo de uso**:
```python
dynamodb = get_dynamodb_resource()
```

**Notas de implementación**:
- Lee la región de la variable de entorno `AWS_REGION`
- Usa `eu-west-1` (Europa - Irlanda) como región por defecto
- Para usar DynamoDB local en Docker, la URL endpoint sería `http://dynamodb-local:8000`

---

### `create_tables()`

Crea las tablas de DynamoDB necesarias para el proyecto. Gestiona errores gracefully si las tablas ya existen.

**Parámetros**: Ninguno

**Retorna**: None

**Ejemplo de uso**:
```python
if __name__ == "__main__":
    create_tables()
```

## Tablas de DynamoDB

### 1. **SpacegomPlanets**

Tabla simple con clave primaria única para almacenar datos de planetas.

**Estructura**:
```
TableName: SpacegomPlanets
Partition Key: planet_code (String)
```

**Ejemplo de item**:
```json
{
  "planet_code": "632",
  "area": 3,
  "world_density": "Baja",
  "tech_level": 5,
  "population": 8000000
}
```

**Características**:
- **ReadCapacityUnits**: 5
- **WriteCapacityUnits**: 5
- **Tipo de clave**: Hash (Partition Key simple)

---

### 2. **SpacegomGames**

Tabla con Single Table Design (PK + SK) para almacenar toda la información relacionada con juegos.

**Estructura**:
```
TableName: SpacegomGames
Partition Key: game_id (String)
Sort Key: entity_id (String)
```

**Ejemplo de items**:
```json
{
  "game_id": "infini_group",
  "entity_id": "GAME_STATE",
  "company_name": "Infini Group",
  "ship_name": "North Star",
  "created_at": "2026-01-20T11:47:09.776196"
}
```

```json
{
  "game_id": "infini_group",
  "entity_id": "PLAYER_1",
  "name": "Widaker Farq",
  "role": "Director gerente",
  "salary": 20
}
```

```json
{
  "game_id": "infini_group",
  "entity_id": "TRANSACTION_001",
  "type": "trade",
  "amount": -90,
  "description": "Compra 10 UCN de INDU"
}
```

**Características**:
- **ReadCapacityUnits**: 5
- **WriteCapacityUnits**: 5
- **Diseño**: Single Table Design (múltiples tipos de entidades)
- **Ventajas**: Permite queries eficientes por `game_id` y filtrado por `entity_id`

**Patrones de entity_id sugeridos**:
- `GAME_STATE`: Estado del juego
- `PLAYER_{n}`: Información de jugador
- `TRANSACTION_{id}`: Transacciones financieras
- `MISSION_{id}`: Misiones
- `CARGO_{id}`: Items de carga

## Manejo de Errores

El módulo captura excepciones de `ClientError` de botocore:

```python
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("⚠️ Tabla ya existe. Omitiendo.")
    else:
        print(f"❌ Error crítico: {e}")
```

**Códigos de error comunes**:
- `ResourceInUseException`: La tabla ya existe
- `ResourceNotFoundException`: La tabla no existe
- `ValidationException`: Error de validación en parámetros
- `ThrottlingException`: Límite de throughput excedido

## Variables de Entorno

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `AWS_REGION` | `eu-west-1` | Región de AWS para DynamoDB |
| `AWS_ACCESS_KEY_ID` | - | Clave de acceso de AWS (requerida en AWS real) |
| `AWS_SECRET_ACCESS_KEY` | - | Clave secreta de AWS (requerida en AWS real) |

## Uso en Desarrollo

### Local con DynamoDB Local (Docker)

1. Configurar variable de entorno:
```bash
export AWS_REGION=us-east-1  # DynamoDB local usa esta región
```

2. Ejecutar el script:
```bash
source .venv/bin/activate
python app/aws_setup.py
```

### En AWS Real

1. Configurar credenciales de AWS:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=eu-west-1
```

2. Ejecutar el script:
```bash
python app/aws_setup.py
```

## Consideraciones de Diseño

### Single Table Design (SpacegomGames)

La tabla `SpacegomGames` utiliza el patrón Single Table Design de DynamoDB, que permite:

1. **Transacciones atómicas**: Múltiples items relacionados en una única tabla
2. **Queries eficientes**: Recuperar todos los datos de un juego con una sola consulta
3. **Escalabilidad**: Mejor rendimiento que múltiples tablas
4. **Flexibilidad**: Fácil agregar nuevos tipos de entidades

### Estructura de Clave Compuesta

```
PK (Partition Key): game_id
    └─ SK (Sort Key): entity_id
```

Esto permite patrones de consulta como:
- Obtener todo de un juego: `game_id = "infini_group"`
- Obtener solo jugadores: `game_id = "infini_group" AND begins_with(entity_id, "PLAYER_")`
- Obtener transacciones: `game_id = "infini_group" AND begins_with(entity_id, "TRANSACTION_")`

## Futuras Mejoras

- [ ] Implementar Global Secondary Indexes (GSI) para queries por `entity_id`
- [ ] Agregar TTL (Time To Live) para datos temporales
- [ ] Implementar backup automático
- [ ] Agregar encriptación en tránsito y en reposo
- [ ] Implementar puntos de recuperación (point-in-time recovery)
- [ ] Agregar CloudWatch alarms para monitoreo

## Integración con la Aplicación

Este módulo debería integrarse con:

1. **`app/main.py`**: Endpoints para crear/eliminar juegos
2. **`app/game_state.py`**: Migración de persistencia JSON a DynamoDB
3. **`app/database.py`**: Sincronización con SQLite/SQLAlchemy (si se mantiene)

## Próximas Fases

### Fase 1: Infraestructura Base ✅
- Crear tablas de DynamoDB
- Configurar acceso a AWS

### Fase 2: Migración de Datos
- Migrar estado del juego desde JSON a DynamoDB
- Implementar sincronización bidireccional

### Fase 3: Optimización
- Implementar índices secundarios
- Optimizar throughput
- Implementar caching

### Fase 4: Observabilidad
- Agregar logging detallado
- Implementar CloudWatch metrics
- Agregar distributed tracing

## Referencias

- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Boto3 DynamoDB Resource](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)
- [DynamoDB Single Table Design](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)