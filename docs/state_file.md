# Archivo de Estado del Juego (state.json)

## Descripción General

El archivo `state.json` es el archivo principal que contiene todo el estado persistente de una partida de SpaceGOM. Se encuentra en `data/games/{game_id}/state.json` y se actualiza automáticamente cada vez que el estado del juego cambia.

## Estructura General

```json
{
  "game_id": "string",
  "created_at": "ISO8601_datetime",
  "updated_at": "ISO8601_datetime",
  // ... resto de campos
}
```

## Campos Principales

### Información Básica del Juego

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `game_id` | string | Identificador único de la partida |
| `created_at` | string | Fecha de creación en formato ISO8601 |
| `updated_at` | string | Última actualización en formato ISO8601 |
| `difficulty` | string | Nivel de dificultad ("easy", "normal", "hard") |

### Configuración Inicial

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `area` | integer | Área galáctica donde se desarrolla el juego (1-6) |
| `world_density` | string | Densidad de mundos ("Baja", "Media", "Alta") |
| `setup_complete` | boolean | Indica si la configuración inicial está completa |

### Nave y Posicionamiento

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `ship_row` | integer | Fila actual de la nave en el mapa galáctico |
| `ship_col` | integer | Columna actual de la nave en el mapa galáctico |
| `ship_pos_complete` | boolean | Indica si la posición inicial está establecida |
| `ship_location_on_planet` | string | Ubicación específica en el planeta ("Mundo", "Estación", etc.) |
| `company_name` | string | Nombre de la empresa |
| `ship_name` | string | Nombre de la nave |
| `ship_model` | string | Modelo de la nave |

### Recursos de la Nave

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `passengers` | integer | Número actual de pasajeros |
| `fuel` | integer | Combustible actual |
| `fuel_max` | integer | Capacidad máxima de combustible |
| `storage` | integer | Almacenamiento actual utilizado |
| `storage_max` | integer | Capacidad máxima de almacenamiento |

### Tiempo y Progreso

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `month` | integer | Mes actual del juego |
| `year` | integer | Año actual del juego |
| `day` | integer | Día actual del mes |
| `reputation` | integer | Puntuación de reputación |

### Sistema de Eventos

#### Cola de Eventos (`event_queue`)
Array de eventos programados para ejecutarse en el futuro.

```json
{
  "id": 1,
  "type": "salary_payment",
  "date": "35-01-1",
  "data": {
    "monthly_payment": true
  }
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del evento |
| `type` | string | Tipo de evento ("salary_payment", "mission_deadline", etc.) |
| `date` | string | Fecha programada en formato "DD-MM-YY" |
| `data` | object | Datos específicos del evento |

### Sistema de Daños

```json
{
  "damages": {
    "light": false,
    "moderate": false,
    "severe": false,
    "counts": {
      "light": 0,
      "moderate": 0,
      "severe": 0
    }
  }
}
```

### Exploración y Navegación

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `current_planet_code` | integer | Código del planeta actual |
| `starting_planet_code` | integer | Código del planeta de inicio |
| `current_area` | integer | Área actual |
| `explored_quadrants` | array | Lista de cuadrantes explorados (formato "row,col") |
| `quadrant_planets` | object | Mapa de cuadrantes a códigos de planetas |
| `discovered_planets` | object | Planetas descubiertos con información adicional |

### Sistema Económico

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `treasury` | integer | Fondos disponibles en SC (Space Credits) |

#### Transacciones (`transactions`)
Historial de todas las transacciones económicas.

```json
{
  "date": "2026-01-20T11:49:52.650861",
  "amount": -90,
  "description": "Compra 10 UCN de INDU",
  "category": "Comercio"
}
```

### Carga y Comercio

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `cargo` | object | Carga actual en la bodega (productos y cantidades) |

### Sistema de Eventos y Logs

#### Eventos (`events`)
Registro de eventos importantes del juego con timestamps.

```json
{
  "timestamp": "2026-01-20T11:47:13.890518",
  "type": "initial_setup",
  "description": "Empresa establecida en Área 3 con densidad de mundos Media",
  "data": {
    "area": 3,
    "world_density": "Media",
    "area_roll": [2, 1],
    "density_roll": [2, 4]
  }
}
```

#### Tiradas de Dados (`dice_rolls`)
Historial completo de todas las tiradas de dados realizadas.

```json
{
  "timestamp": "2026-01-20T11:47:13.889465",
  "num_dice": 2,
  "results": [2, 1],
  "total": 3,
  "is_manual": false,
  "purpose": "initial_area"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `timestamp` | string | Momento exacto de la tirada |
| `num_dice` | integer | Número de dados tirados |
| `results` | array | Resultados individuales de cada dado |
| `total` | integer | Suma total de la tirada |
| `is_manual` | boolean | Si fue una tirada manual o automática |
| `purpose` | string | Propósito de la tirada ("initial_area", "world_density", etc.) |

### Logs de Eventos (`event_logs`)
Mensajes de log para mostrar al usuario, organizados por fecha del juego.

```json
{
  "game_date": "01-01-1",
  "timestamp": "2026-01-20T11:47:51.480888",
  "message": "📜 La empresa Infini Group inicia sus operaciones...",
  "type": "success"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `game_date` | string | Fecha del juego en formato "DD-MM-YY" |
| `timestamp` | string | Timestamp real en ISO8601 |
| `message` | string | Mensaje descriptivo con emojis |
| `type` | string | Tipo de mensaje ("success", "info", "warning", "error") |

### Transporte de Pasajeros

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `passenger_transport_available` | boolean | Si el transporte de pasajeros está disponible |

## Ejemplo Completo

```json
{
  "game_id": "infini_group",
  "created_at": "2026-01-20T11:47:09.776196",
  "updated_at": "2026-01-20T11:50:20.542396",
  "area": 3,
  "world_density": "Baja",
  "setup_complete": true,
  "ship_row": 5,
  "ship_col": 6,
  "ship_pos_complete": true,
  "ship_location_on_planet": "Mundo",
  "company_name": "Infini Group",
  "ship_name": "North Star",
  "ship_model": "Basic Starfall",
  "passengers": 6,
  "fuel": 18,
  "fuel_max": 30,
  "storage": 0,
  "storage_max": 40,
  "month": 1,
  "reputation": 0,
  "year": 1,
  "day": 1,
  "difficulty": "normal",
  "treasury": 416,
  "current_planet_code": 632,
  "starting_planet_code": 632,
  "current_area": 3,
  "passenger_transport_available": true
}
```

## Notas de Implementación

- El archivo se actualiza automáticamente cada vez que cambia el estado del juego
- Los timestamps están en UTC y formato ISO8601
- Las fechas del juego usan el formato "DD-MM-YY" para facilitar la lectura
- Los eventos se procesan en orden cronológico
- El historial de tiradas de dados se mantiene completo para auditoría y debugging
- Los logs de eventos incluyen emojis para mejorar la UX en la interfaz

## Campos Opcionales y Extensibles

El archivo está diseñado para ser extensible. Nuevos campos pueden agregarse según se implementen nuevas funcionalidades del juego sin romper la compatibilidad con versiones anteriores.