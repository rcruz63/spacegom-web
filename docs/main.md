# main.py - API Principal de FastAPI

## Overview

Este es el archivo principal de la aplicación FastAPI que contiene todos los endpoints de la API REST. Actúa como el punto de entrada principal del backend, manejando rutas web, API endpoints, y la lógica de negocio principal.

**Ubicación**: `app/main.py`
**Líneas**: 2216
**Dependencias**: FastAPI, SQLAlchemy, Jinja2, módulos internos

## Inicialización

```python
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup_event():
    init_db()
```

## Endpoints Web (Páginas HTML)

### Páginas Principales
- `GET /` → `index.html` - Página de inicio
- `GET /dashboard` → `dashboard.html` - Panel de control principal
- `GET /setup` → `setup.html` - Configuración inicial de partida
- `GET /personnel` → `personnel.html` - Gestión de personal
- `GET /treasury` → `treasury.html` - Finanzas y tesorería
- `GET /missions` → `missions.html` - Gestión de misiones
- `GET /logs` → `logs.html` - Historial de eventos
- `GET /trade` → `trade.html` - Terminal comercial

## API Endpoints

### Gestión de Juegos

#### `GET /api/games`
Lista todos los juegos disponibles.
**Retorno**: `{"games": [lista de juegos]}`

#### `POST /api/games/new`
Crea un nuevo juego.
**Parámetros**: `game_name` (opcional)
**Retorno**: `{"game_id": str, "state": dict}`

#### `GET /api/games/{game_id}`
Obtiene el estado completo del juego incluyendo estadísticas de nave.
**Retorno**: `{"state": dict, "ship_stats": dict}`

#### `POST /api/games/{game_id}/update`
Actualiza campos del estado del juego (combustible, almacenamiento, etc.).
**Parámetros**: `fuel`, `storage`, `month`, `reputation`, `damage_*`
**Retorno**: `{"state": dict}`

#### `GET /api/games/{game_id}/logs`
Obtiene logs de eventos del juego.
**Parámetros**: `limit`, `event_type`
**Retorno**: `{"logs": list, "count": int}`

### Setup y Configuración

#### `POST /api/games/{game_id}/setup`
Setup inicial: área, densidad de mundos.
**Parámetros**: `area_manual`, `density_manual`
**Retorno**: Resultados de tiradas y estado

#### `POST /api/games/{game_id}/setup-position`
Posición inicial de nave (1d6 para fila y columna).
**Parámetros**: `row_manual`, `col_manual`
**Retorno**: Posición y estado

#### `POST /api/games/{game_id}/company-setup`
Configuración de compañía y nave.
**Parámetros**: `company_name`, `ship_name`, `ship_model`
**Retorno**: Estado actualizado

#### `POST /api/games/{game_id}/complete-setup`
Completa setup con dificultad y crea personal inicial.
**Parámetros**: `difficulty` ("easy"/"normal"/"hard")
**Retorno**: Configuración final

### Navegación y Exploración

#### `POST /api/games/{game_id}/update-location`
Actualiza ubicación de nave en planeta.
**Parámetros**: `location`
**Retorno**: `{"status": "success", "location": str}`

#### `POST /api/games/{game_id}/explore`
Marca cuadrante como explorado.
**Parámetros**: `row`, `col`
**Retorno**: Estado de exploración

#### `POST /api/games/{game_id}/navigate-area`
Navega a área adyacente.
**Parámetros**: `direction` ("prev"/"next")
**Retorno**: Nueva área

#### `GET /api/games/{game_id}/area/{area_number}/planets`
Obtiene planetas descubiertos en área específica.
**Retorno**: Lista de planetas con datos completos

### Sistema de Dados

#### `POST /api/roll-dice` (Legacy)
Tirada simple de dados para HTMX.
**Parámetros**: `num_dices`, `manual_result`
**Retorno**: HTML con resultado

#### `POST /api/dice/roll`
Endpoint universal de tiradas de dados.
**Parámetros**: JSON con `num_dice`, `dice_sides`, `manual_values`
**Retorno**: `{"dice": list, "sum": int, "mode": str}`

#### `POST /api/games/{game_id}/roll`
Tirada de dados registrada en historial del juego.
**Parámetros**: `num_dice`, `manual_results`, `purpose`
**Retorno**: Resultados y total

#### `POST /api/games/{game_id}/roll-planet-code`
Genera código de planeta con 3d6 y obtiene datos.
**Parámetros**: `manual_results`
**Retorno**: Código, dados, datos del planeta

### Gestión de Personal

#### `GET /api/games/{game_id}/personnel`
Obtiene todo el personal activo.
**Retorno**: Lista de empleados con salarios totales

#### `POST /api/games/{game_id}/personnel`
Contrata nuevo personal.
**Parámetros**: `position`, `name`, `monthly_salary`, `experience`, `morale`
**Retorno**: Datos del nuevo empleado

#### `PUT /api/games/{game_id}/personnel/{employee_id}`
Actualiza información de empleado.
**Parámetros**: Campos a actualizar
**Retorno**: Empleado actualizado

#### `DELETE /api/games/{game_id}/personnel/{employee_id}`
Despide empleado (marca como inactivo).

### Sistema de Contratación

#### `GET /api/games/{game_id}/hire/available-positions`
Obtiene posiciones disponibles para contratar basadas en nivel tech del planeta.
**Retorno**: Lista de posiciones con requisitos

#### `POST /api/games/{game_id}/hire/start`
Inicia búsqueda de contratación.
**Parámetros**: `position`, `experience_level`, `manual_dice_days`
**Retorno**: Detalles de la tarea creada

#### `GET /api/games/{game_id}/personnel/{employee_id}/tasks`
Obtiene tareas de un empleado (principalmente Director Gerente).
**Retorno**: Tareas actuales, pendientes y completadas

#### `PUT /api/games/{game_id}/tasks/{task_id}/reorder`
Reordena tarea pendiente en cola.
**Parámetros**: `new_position`

#### `DELETE /api/games/{game_id}/tasks/{task_id}`
Elimina tarea pendiente.

### Tesorería

#### `GET /api/games/{game_id}/treasury`
Obtiene información financiera.
**Retorno**: Balance, gastos mensuales, transacciones recientes

#### `POST /api/games/{game_id}/treasury/transaction`
Agrega transacción financiera.
**Parámetros**: `amount`, `description`, `category`
**Retorno**: Nuevo balance

### Misiones

#### `GET /api/games/{game_id}/missions`
Obtiene todas las misiones categorizadas por estado.
**Retorno**: Misiones activas, completadas, fallidas

#### `POST /api/games/{game_id}/missions`
Crea nueva misión (campaña o especial).
**Parámetros**: `mission_type`, `objective_number` o `mission_code`/`book_page`, etc.
**Retorno**: ID de misión creada

#### `PUT /api/games/{game_id}/missions/{mission_id}`
Actualiza resultado de misión.
**Parámetros**: `result`, `completed_date`

#### `POST /api/games/{game_id}/missions/{mission_id}/resolve`
Resuelve deadline de misión.
**Parámetros**: `success`

#### `DELETE /api/games/{game_id}/missions/{mission_id}`
Elimina misión.

### Planetas

#### `GET /api/planets/{code}`
Obtiene datos de planeta por código.
**Retorno**: Datos formateados y validación de inicio

#### `GET /api/planets`
Busca planetas por nombre.
**Parámetros**: `name`

#### `POST /api/games/{game_id}/set-starting-planet`
Establece planeta inicial del juego.
**Parámetros**: `code`

#### `GET /api/planets/next/{current_code}`
Obtiene siguiente planeta en secuencia 3d6.
**Retorno**: Planeta siguiente con validación

#### `POST /api/planets/{code}/update-notes`
Actualiza notas de planeta.
**Parámetros**: `notes`

#### `POST /api/planets/{code}/update-bootstrap`
Actualiza datos faltantes para validación de bootstrap.
**Parámetros**: `tech_level`, `population_over_1000`

### Sugerencias de Nombres

#### `GET /api/suggestions/company-name`
Retorna nombre de compañía aleatorio.

#### `GET /api/suggestions/ship-name`
Retorna nombre de nave aleatorio.

### Transporte de Pasajeros

#### `GET /api/games/{game_id}/passenger-transport/info`
Obtiene información para acción de transporte de pasajeros.
**Retorno**: Capacidad, modificadores, etc.

#### `POST /api/games/{game_id}/passenger-transport/execute`
Ejecuta transporte de pasajeros.
**Parámetros**: `manual_dice`
**Retorno**: Resultados de dados, pasajeros, ingresos

### Comercio

#### `GET /api/games/{game_id}/trade/market`
Obtiene productos disponibles para comprar/vender.
**Retorno**: Datos del mercado

#### `GET /api/games/{game_id}/trade/orders`
Obtiene todas las órdenes de comercio.

#### `POST /api/games/{game_id}/trade/negotiate`
Simula negociación de precios.
**Parámetros**: `action` ("buy"/"sell"), `manual_roll`
**Retorno**: Modificadores y resultado

#### `POST /api/games/{game_id}/trade/buy`
Ejecuta compra de productos.
**Parámetros**: `planet_code`, `product_code`, `quantity`, `unit_price`

#### `POST /api/games/{game_id}/trade/sell`
Ejecuta venta de productos.
**Parámetros**: `order_id`, `planet_code`, `sell_price_total`

### Sistema de Tiempo

#### `POST /api/games/{game_id}/time/advance`
Avanza tiempo al próximo evento y lo procesa.
**Parámetros**: `manual_dice`
**Retorno**: Resultado del evento procesado

## Funciones Auxiliares

### `format_planet_data(planet: Planet) -> dict`
Formatea datos de planeta para respuestas API con valores legibles.

### `is_valid_starting_planet(planet: Planet) -> dict`
Verifica si planeta es válido para inicio según reglas del juego.

## Dependencias

- **FastAPI**: Framework web
- **SQLAlchemy**: ORM para BD
- **Jinja2**: Templates HTML
- **Módulos internos**: `database`, `game_state`, `dice`, `time_manager`, `name_suggestions`, etc.

## Notas de Implementación

- **HTMX Integration**: Muchos endpoints retornan HTML para actualizaciones dinámicas
- **Event System**: Integración con `event_handlers` y `event_logger`
- **Dice System**: Uso extensivo de `DiceRoller` para todas las mecánicas aleatorias
- **State Management**: `GameState` maneja persistencia JSON
- **Database**: SQLite con modelos en `database.py`
- **Time Management**: Sistema complejo con eventos programados

## Mejores Prácticas

- Usar `Depends(get_db)` para inyección de sesión DB
- Manejar errores con `HTTPException`
- Registrar tiradas de dados con `game.record_dice_roll()`
- Loggear eventos importantes con `EventLogger`
- Validar parámetros de entrada
- Mantener consistencia en formato de respuestas JSON