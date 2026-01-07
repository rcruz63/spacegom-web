# API Documentation - Spacegom

## 🎮 Game Management

### List All Games
```http
GET /api/games
```

### Create New Game
```http
POST /api/games/new
Content-Type: application/x-www-form-urlencoded

game_name=my_campaign (optional)
```

### Get Game State
```http
GET /api/games/{game_id}
```

### Update Game State
```http
POST /api/games/{game_id}/update
Content-Type: application/x-www-form-urlencoded

fuel=20
storage=15
month=3
reputation=2
damage_light=true
damage_moderate=false
damage_severe=false
```

## 🎲 Dice Rolling

### Roll Dice (General)
```http
POST /api/games/{game_id}/roll
Content-Type: application/x-www-form-urlencoded

num_dice=3
manual_results=4,6,6  (optional, comma-separated)
purpose=combat
```

**Response:**
```json
{
  "results": [4, 6, 6],
  "total": 16,
  "is_manual": true,
  "purpose": "combat",
  "formatted": "4 + 6 + 6"
}
```

### Roll for Planet Code
```http
POST /api/games/{game_id}/roll-planet-code
Content-Type: application/x-www-form-urlencoded

manual_results=4,6,6  (optional)
```

**Response:**
```json
{
  "code": 466,
  "dice": [4, 6, 6],
  "planet": {
    "code": 466,
    "name": "Bretobos",
    "spaceport": "MED-DB-2",
    "orbital_facilities": "CC",
    "life_support": {...},
    "products": {...}
  }
}
```

## 🌍 Planets

### Get Planet by Code
```http
GET /api/planets/466
```

### Search Planets
```http
GET /api/planets?name=breto
```

## 🗺️ Exploration

### Mark Quadrant as Explored
```http
POST /api/games/{game_id}/explore
Content-Type: application/x-www-form-urlencoded

row=2
col=3
```

## Example cURL Commands

```bash
# Create a new game
curl -X POST http://localhost:8000/api/games/new \
  -F "game_name=test_campaign"

# Roll for planet code
curl -X POST http://localhost:8000/api/games/test_campaign/roll-planet-code

# Get planet info
curl http://localhost:8000/api/planets/466

# Update game state
curl -X POST http://localhost:8000/api/games/test_campaign/update \
  -F "fuel=25" \
  -F "reputation=3"
```
