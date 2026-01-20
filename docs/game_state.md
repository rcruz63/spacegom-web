# game_state.py - Gestión del Estado del Juego

## Overview

Este módulo maneja la persistencia del estado del juego usando archivos JSON. Cada partida tiene su propio directorio con un archivo `state.json` que contiene todo el estado persistente.

**Ubicación**: `app/game_state.py`
**Líneas**: 262
**Dependencias**: `json`, `os`, `pathlib`, `datetime`

## Clase GameState

### Inicialización

```python
class GameState:
    GAMES_DIR = "data/games"
    
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.game_dir = Path(self.GAMES_DIR) / game_id
        self.state_file = self.game_dir / "state.json"
        self.state = self._load_or_create_state()
```

### Estado por Defecto

El estado inicial incluye campos para:
- **Setup**: Área, densidad de mundos, posición inicial
- **Compañía/Nave**: Nombres, modelo, pasajeros
- **HUD**: Combustible, almacenamiento, mes, reputación
- **Calendario**: Año, mes, día, cola de eventos
- **Daños**: Sistema de daños leves/moderados/graves
- **Navegación**: Planetas descubiertos, cuadrantes explorados
- **Economía**: Dificultad, tesorería, transacciones
- **Historial**: Eventos y tiradas de dados

### Métodos Principales

#### `save()`
Guarda el estado actual en `state.json` con timestamp actualizado.

#### `update(**kwargs)`
Actualiza múltiples campos del estado y guarda automáticamente.

#### `add_event(event_type: str, description: str, data: dict = None)`
Agrega evento al historial de eventos.

#### `record_dice_roll(num_dice: int, results: list, is_manual: bool, purpose: str = "")`
Registra tirada de dados en historial.

#### `explore_quadrant(row: int, col: int)`
Marca cuadrante como explorado y resetea flags de acciones.

#### `discover_planet(row: int, col: int, planet_code: int)`
Registra descubrimiento de planeta en cuadrante específico.

#### `get_adjacent_coordinates(row: int, col: int, jump_range: int = 1)`
Calcula coordenadas alcanzables dentro del rango de salto, incluyendo transiciones entre áreas.

### Métodos de Clase

#### `list_games() -> list`
Lista todas las partidas disponibles con metadata básica.

#### `create_new_game(game_name: str = None) -> GameState`
Crea nueva partida con ID único.

## Estructura del Estado JSON

```json
{
  "game_id": "string",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime",
  
  "area": 7,
  "world_density": "Media",
  "setup_complete": true,
  
  "ship_row": 3,
  "ship_col": 4,
  "ship_location_on_planet": "Espaciopuerto",
  
  "company_name": "Space Explorers Inc",
  "ship_name": "Star Voyager",
  "ship_model": "Basic Starfall",
  "passengers": 5,
  
  "fuel": 25,
  "fuel_max": 30,
  "storage": 15,
  "storage_max": 40,
  "month": 3,
  "reputation": 2,
  
  "year": 1,
  "day": 15,
  "event_queue": [...],
  
  "damages": {
    "light": false,
    "moderate": true,
    "severe": false,
    "counts": {"light": 2, "moderate": 1, "severe": 0}
  },
  
  "explored_quadrants": ["1,2", "1,3", "2,2"],
  "quadrant_planets": {"1,2": 123},
  "discovered_planets": {"123": {"area": 7, "quadrant": "1,2"}},
  
  "difficulty": "normal",
  "treasury": 450,
  "transactions": [...],
  
  "events": [...],
  "dice_rolls": [...]
}
```

## Dependencias

- **pathlib.Path**: Manejo de rutas de archivos
- **json**: Serialización/deserialización
- **datetime**: Timestamps

## Notas de Implementación

- **Persistencia**: Estado guardado automáticamente en operaciones críticas
- **Thread Safety**: No implementada (FastAPI maneja concurrencia)
- **Validación**: Campos actualizados sin validación (manejar en endpoints)
- **Event Queue**: Lista ordenada de eventos futuros
- **Coordinate System**: 1-based para display, 0-based para cálculos internos

## Mejores Prácticas

- Usar `update()` para cambios múltiples
- Registrar eventos importantes con `add_event()`
- Siempre llamar `save()` después de modificar estado
- Validar coordenadas antes de usar métodos de navegación
- Mantener consistencia entre `explored_quadrants` y `quadrant_planets`