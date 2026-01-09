# API Documentation - Spacegom

Este documento detalla todos los endpoints de la API REST de Spacegom Companion.

## 🎮 Game Management

### List All Games
```http
GET /api/games
```
Retorna una lista de todas las partidas guardadas.

---

### Create New Game
```http
POST /api/games/new
Content-Type: application/x-www-form-urlencoded

game_name=my_campaign (optional)
```
Crea una nueva partida y retorna el `game_id`.

---

### Get Game State
```http
GET /api/games/{game_id}
```
Retorna el estado completo del juego incluyendo las estadísticas de la nave.

**Response:**
```json
{
  "state": {
    "game_id": "...",
    "fuel": 18,
    "storage": 16,
    "company_name": "...",
    "ship_name": "...",
    "ship_model": "Basic Starfall",
    ...
  },
  "ship_stats": {
    "jump": 1,
    "passengers": 10,
    "storage": 40,
    ...
  }
}
```

---

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
Actualiza campos específicos del estado del juego.

---

### Company Setup
```http
POST /api/games/{game_id}/company-setup
Content-Type: application/x-www-form-urlencoded

company_name=Nebula Traders
ship_name=Phoenix
ship_model=Basic Starfall
```
Guarda los detalles de la compañía y nave del jugador.

---

### Initial Setup (Area & Density)
```http
POST /api/games/{game_id}/setup
Content-Type: application/x-www-form-urlencoded

area_manual=4,5 (optional)
density_manual=6,3 (optional)
```
Determina el área espacial (2d6) y la densidad de mundos (2d6).

**Response:**
```json
{
  "area": {
    "value": 9,
    "dice": [4, 5],
    "is_manual": true
  },
  "world_density": {
    "level": "Media",
    "total": 9,
    "dice": [6, 3],
    "is_manual": true
  }
}
```

---

### Setup Ship Position
```http
POST /api/games/{game_id}/setup-position
Content-Type: application/x-www-form-urlencoded

row_manual=3 (optional)
col_manual=4 (optional)
```
Determina la posición inicial de la nave en el grid 6x6.

**Response:**
```json
{
  "row": 3,
  "col": 4,
  "col_letter": "D",
  "ship_pos_complete": true
}
```

---

### Set Starting Planet
```http
POST /api/games/{game_id}/set-starting-planet
Content-Type: application/x-www-form-urlencoded

code=123
```
Establece el planeta de origen para el juego.

---

### Complete Setup with Difficulty
```http
POST /api/games/{game_id}/complete-setup
Content-Type: application/x-www-form-urlencoded

difficulty=normal
```
Completa la configuración inicial del juego seleccionando dificultad, creando 11 empleados iniciales y asignando fondos.

**Difficulty Levels:**
- `easy`: 600 SC iniciales
- `normal`: 500 SC iniciales  
- `hard`: 400 SC iniciales

**Response:**
```json
{
  "status": "success",
  "difficulty": "normal",
  "starting_funds": 500,
  "personnel_count": 11,
  "monthly_salaries": 76
}
```

---

### Update Ship Location on Planet
```http
POST /api/games/{game_id}/update-location
Content-Type: application/x-www-form-urlencoded

location=Mundo|Puerto|Orbital|Estacion
```
Actualiza la ubicación de la nave en el planeta actual.

---

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

---

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
    "products": {...},
    "bootstrap_data": {
      "tech_level": "ES",
      "population_over_1000": true,
      "convenio_spacegom": true
    }
  },
  "is_valid_start": {
    "is_valid": true,
    "checks": {
      "population": true,
      "tech_level": true,
      "life_support": true,
      "convenio": true,
      "has_product": true
    }
  }
}
```

---

## 🌍 Planets

### Get Planet by Code
```http
GET /api/planets/{code}
```
Obtiene información detallada de un planeta por su código (111-666).

**Example:**
```http
GET /api/planets/466
```

**Response:**
```json
{
  "planet": {
    "code": 466,
    "name": "Bretobos",
    "spaceport": "MED-DB-2",
    "orbital_facilities": "CC",
    "life_support": {
      "1": "RF",
      "2": "RF",
      ...
    },
    "products": {
      "INDU": true,
      "BASI": false,
      ...
    },
    "bootstrap_data": {
      "tech_level": "ES",
      "population_over_1000": true,
      "convenio_spacegom": true
    }
  },
  "is_valid_start": {
    "is_valid": true,
    "checks": {...}
  }
}
```

---

### Get Next Planet (Consecutive Search)
```http
GET /api/planets/next/{current_code}
```
**Nuevo en v0.2**: Obtiene el siguiente planeta en la secuencia 3d6 (111 → 112 → 113...).

**Example:**
```http
GET /api/planets/next/115
```

**Response:**
```json
{
  "planet": {
    "code": 116,
    "name": "...",
    ...
  },
  "is_valid_start": {...}
}
```

---

### Search Planets by Name
```http
GET /api/planets?name=breto
```
Busca planetas por nombre (máximo 50 resultados).

**Response:**
```json
{
  "planets": [
    {
      "code": 466,
      "name": "Bretobos",
      "spaceport": "MED-DB-2"
    }
  ]
}
```

---

### Update Planet Bootstrap Data
```http
POST /api/planets/{code}/update-bootstrap
Content-Type: application/x-www-form-urlencoded

tech_level=ES
population_over_1000=true
```
Actualiza datos faltantes de un planeta (nivel tecnológico y población).

---

## 🗺️ Exploration

### Mark Quadrant as Explored
```http
POST /api/games/{game_id}/explore
Content-Type: application/x-www-form-urlencoded

row=2
col=3
```
Marca un cuadrante como explorado.

**Response:**
```json
{
  "explored": true,
  "quadrant": "2,3",
  "explored_quadrants": [...]
}
```

---

### Update Planet Notes
```http
POST /api/planets/{code}/update-notes
Content-Type: application/x-www-form-urlencoded

notes=Este planeta tiene excelentes recursos mineros
```
Actualiza las notas personalizadas de un planeta.

**Response:**
```json
{
  "status": "success",
  "planet": {
    "code": 466,
    "name": "Bretobos",
    "notes": "Este planeta tiene excelentes recursos mineros",
    ...
  }
}
```

---

## 👥 Personnel Management

### Get Personnel List
```http
GET /api/games/{game_id}/personnel
```
Retorna la lista de empleados activos del juego.

**Response:**
```json
{
  "personnel": [
    {
      "id": 1,
      "position": "Director gerente",
      "name": "Widaker Farq",
      "monthly_salary": 20,
      "experience": "V",
      "morale": "A",
      "hire_date": "2026-01-08",
      "notes": ""
    }
  ],
  "total_monthly_salaries": 76,
  "count": 11
}
```

---

### Hire Personnel
```http
POST /api/games/{game_id}/personnel
Content-Type: application/x-www-form-urlencoded

position=Piloto
name=Juan García
monthly_salary=10
experience=E
morale=M
notes=Piloto experimental
```
Contrata un nuevo empleado.

**Experience Levels:**
- `N`: Novato
- `E`: Experto
- `V`: Veterano

**Morale Levels:**
- `B`: Baja
- `M`: Media
- `A`: Alta

**Response:**
```json
{
  "status": "success",
  "employee": {
    "id": 12,
    "name": "Juan García",
    "position": "Piloto"
  }
}
```

---

### Update Personnel
```http
PUT /api/games/{game_id}/personnel/{employee_id}
Content-Type: application/x-www-form-urlencoded

monthly_salary=12
morale=A
```
Actualiza la información de un empleado (campos opcionales).

**Response:**
```json
{
  "status": "success",
  "employee": {
    "id": 12,
    "name": "Juan García"
  }
}
```

---

### Fire Personnel
```http
DELETE /api/games/{game_id}/personnel/{employee_id}
```
Despide un empleado (marca como inactivo).

**Response:**
```json
{
  "status": "success",
  "message": "Juan García has been dismissed"
}
```

---

## 💰 Treasury Management

### Get Treasury Status
```http
GET /api/games/{game_id}/treasury
```
Obtiene el estado financiero completo del juego.

**Response:**
```json
{
  "current_balance": 500,
  "difficulty": "normal",
  "reputation": 0,
  "monthly_expenses": {
    "salaries": 76,
    "loans": 0,
    "total": 76
  },
  "recent_transactions": [
    {
      "date": "2026-01-08T20:30:00",
      "amount": -50,
      "description": "Compra de combustible",
      "category": "combustible"
    }
  ]
}
```

---

### Add Transaction
```http
POST /api/games/{game_id}/treasury/transaction
Content-Type: application/x-www-form-urlencoded

amount=-50
description=Compra de combustible
category=combustible
```
Registra una transacción financiera (ingreso o gasto).

**Categories:**
- `comercio`: Comercio de productos
- `mision`: Recompensas de misiones
- `suministros`: Compra de suministros
- `reparaciones`: Reparaciones de nave
- `combustible`: Compra de combustible
- `salarios`: Pago de salarios (automático)
- `prestamos`: Préstamos
- `other`: Otros

**Response:**
```json
{
  "status": "success",
  "new_balance": 450,
  "transaction": {
    "date": "2026-01-08T20:30:00",
    "amount": -50,
    "description": "Compra de combustible",
    "category": "combustible"
  }
}
```

---

## 📝 Example cURL Commands

```bash
# Crear una nueva partida
curl -X POST http://localhost:8000/api/games/new \
  -F "game_name=test_campaign"

# Configurar compañía
curl -X POST http://localhost:8000/api/games/test_campaign/company-setup \
  -F "company_name=Nebula Corp" \
  -F "ship_name=Phoenix" \
  -F "ship_model=Basic Starfall"

# Tirar para código de planeta
curl -X POST http://localhost:8000/api/games/test_campaign/roll-planet-code

# Obtener info de planeta
curl http://localhost:8000/api/planets/466

# Buscar siguiente planeta consecutivo
curl http://localhost:8000/api/planets/next/115

# Actualizar estado del juego
curl -X POST http://localhost:8000/api/games/test_campaign/update \
  -F "fuel=25" \
  -F "reputation=3"

# Completar setup con dificultad
curl -X POST http://localhost:8000/api/games/test_campaign/complete-setup \
  -F "difficulty=normal"

# Contratar personal
curl -X POST http://localhost:8000/api/games/test_campaign/personnel \
  -F "position=Piloto" \
  -F "name=Juan García" \
  -F "monthly_salary=10" \
  -F "experience=E" \
  -F "morale=M"

# Ver estado de tesorería
curl http://localhost:8000/api/games/test_campaign/treasury

# Registrar transacción
curl -X POST http://localhost:8000/api/games/test_campaign/treasury/transaction \
  -F "amount=-50" \
  -F "description=Compra de combustible" \
  -F "category=combustible"

# Actualizar notas de planeta
curl -X POST http://localhost:8000/api/planets/466/update-notes \
  -F "notes=Excelente para comercio"
```

---

## 🔄 Códigos de Estado

- `200 OK`: Operación exitosa
- `404 Not Found`: Recurso no encontrado (planeta, partida, etc.)
- `400 Bad Request`: Parámetros inválidos
- `500 Internal Server Error`: Error del servidor
