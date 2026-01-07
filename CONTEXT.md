# Contexto de Desarrollo - Spacegom Companion

> **IMPORTANTE**: Este documento contiene todo el contexto necesario para continuar el desarrollo en otro entorno.

## 📋 Resumen del Proyecto

Aplicación web companion para el juego de mesa/rol **Spacegom**. Sustituye papel y lápiz con un panel interactivo estilo "Spacecraft Control Panel" cyberpunk/espacial.

**Lore**: Has heredado una empresa espacial, una nave y trabajadores tras la muerte de tu madre. Tu objetivo es hacer prosperar la empresa o hundirte en el intento.

---

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** (Python) - Framework web
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos de planetas
- **Pandas + openpyxl** - Para importar Excel

### Frontend
- **TailwindCSS** (CDN) - Estilos cyberpunk/espacial
- **HTMX** - Interactividad
- **HTML + Jinja2** - Templates
- **JavaScript Vanilla** - Lógica del dashboard

### Gestión de Dependencias
- **uv** - Gestor de paquetes Python (NO usar pip)

---

## 📁 Estructura del Proyecto

```
spacegom-web/
├── app/
│   ├── main.py              # FastAPI + todas las rutas API
│   ├── database.py          # Modelos SQLAlchemy (Planet)
│   ├── game_state.py        # Sistema de persistencia JSON
│   ├── dice.py              # Utilidades de dados
│   ├── import_planets.py    # Script para importar Excel
│   └── templates/
│       ├── base.html        # Template base con estilos
│       ├── index.html       # Landing page
│       ├── dashboard.html   # Panel de control principal
│       └── components/      # Componentes HTMX
├── data/
│   ├── spacegom.db          # Base de datos SQLite (generada)
│   ├── Base_de_datos_de_planetas.xlsx  # Excel fuente
│   └── games/               # Partidas guardadas en JSON
│       └── {game_id}/
│           └── state.json
├── .venv/                   # Entorno virtual
├── pyproject.toml           # Dependencias
├── API.md                   # Documentación API
├── README.md                # Documentación general
└── CONTEXT.md               # Este archivo
```

---

## 🚀 Setup Inicial en Nuevo Entorno

### 1. Clonar el repositorio
```bash
git clone <tu-repo>
cd spacegom-web
```

### 2. Instalar uv (si no lo tienes)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Instalar dependencias
```bash
# Activar entorno virtual (CRÍTICO)
source .venv/bin/activate

# Instalar paquetes
uv sync
```

### 4. Verificar que existe el Excel
```bash
ls data/Base_de_datos_de_planetas.xlsx
```

Si NO existe, copiarlo:
```bash
cp /ruta/al/Base_de_datos_de_planetas.xlsx data/
```

### 5. Importar planetas a la base de datos
```bash
# Asegurar entorno activado
source .venv/bin/activate

uv run python app/import_planets.py
```

Debe mostrar: `✅ Importation complete! - Imported: 216 planets`

### 6. Ejecutar servidor
```bash
# IMPORTANTE: Activar entorno si no lo está
source .venv/bin/activate

uv run uvicorn app.main:app --reload --port 8000
```

### 7. Verificar
- Landing: http://localhost:8000
- Dashboard: http://localhost:8000/dashboard
- API Docs: http://localhost:8000/docs (FastAPI automático)

---

## 🎮 Estado Actual del Desarrollo

### ✅ Completado

#### 1. **Infraestructura Base**
- [x] Base de datos SQLite con 216 planetas del Excel
- [x] Sistema de persistencia JSON para múltiples partidas
- [x] Sistema de dados (manual + automático) con historial
- [x] APIs REST completas

#### 2. **Modelos de Datos**

**Planet** (database.py):
- Código (111-666), nombre, espaciopuerto, instalaciones orbitales
- Soporte vital (*1 a *6)
- 13 tipos de productos (INDU, BASI, ALIM, MADE, AGUA, MICO, MIRA, MIPR, PAVA, A, AE, AEI, COM)
- Campos adicionales (*7 a *10)
- Soporte para planetas personalizados

**GameState** (game_state.py):
```python
{
  # Setup Inicial
  "area": None,              # 2-12 (2d6)
  "world_density": None,     # "Baja", "Media", "Alta"
  "setup_complete": False,
  
  # HUD
  "fuel": 18, "fuel_max": 30,
  "storage": 16, "storage_max": 40,
  "month": 1,
  "reputation": 0,
  
  # Daños
  "damages": {"light": False, "moderate": False, "severe": False},
  
  # Navegación
  "current_planet_code": None,
  "current_area": None,
  "explored_quadrants": [],
  
  # Tripulación (3 miembros default)
  "crew": [...],
  "health_level": "MEDIA",
  
  # Finanzas
  "credits": 45230,
  "weekly_expenses": {...},
  "monthly_loans": {...},
  
  # Historial
  "events": [],
  "dice_rolls": []
}
```

#### 3. **Mecánicas de Juego Implementadas**

**Emplazamiento Inicial de la Empresa** ✅
- Endpoint: `POST /api/games/{game_id}/setup`
- Lógica:
  1. Tirar 2d6 → Área del espacio (2-12)
  2. Tirar 2d6 → Densidad de mundos:
     - 2-4: Baja
     - 5-9: Media
     - 10-12: Alta
- Soporte para dados manuales o automáticos
- Todo registrado en historial

#### 4. **Frontend Actual**

**Dashboard** (dashboard.html):
- HUD superior: Combustible, Almacén, Daños, Calendario, Reputación
- Grid 6x6 para navegación con niebla de guerra
- Panel de tripulación con bio-métricas
- Terminal comercial con tabla de mercancías
- **TODO**: Sección de Setup Inicial (siguiente paso)

---

## 🎯 APIs Disponibles

### Gestión de Partidas
```bash
# Listar partidas
GET /api/games

# Crear nueva partida
POST /api/games/new
  -F "game_name=mi_partida"

# Obtener estado
GET /api/games/{game_id}

# Actualizar estado
POST /api/games/{game_id}/update
  -F "fuel=20" -F "reputation=3" ...
```

### Setup Inicial
```bash
# Ejecutar setup (automático)
POST /api/games/{game_id}/setup

# Setup manual
POST /api/games/{game_id}/setup
  -F "area_manual=4,5"        # 2d6 para área
  -F "density_manual=6,3"     # 2d6 para densidad
```

### Dados
```bash
# Tirada general
POST /api/games/{game_id}/roll
  -F "num_dice=2"
  -F "manual_results=4,5"  # opcional
  -F "purpose=combat"

# Tirada para código planetario
POST /api/games/{game_id}/roll-planet-code
  -F "manual_results=4,6,6"  # opcional
```

### Planetas
```bash
# Obtener planeta por código
GET /api/planets/466

# Buscar planetas
GET /api/planets?name=bretobos
```

Ver **API.md** para documentación completa.

---

## 📖 Lógica del Juego

### Flujo de Inicio de Partida

1. **Crear nueva partida**
   ```bash
   POST /api/games/new -F "game_name=campaña_1"
   ```

2. **Emplazamiento Inicial** ✅ IMPLEMENTADO
   ```bash
   POST /api/games/campaña_1/setup
   ```
   - Resultado: Área (2-12), Densidad (Baja/Media/Alta)

3. **Siguiente paso** (PENDIENTE):
   - Determinar planeta inicial (tirar 3d6 para código 111-666)
   - Consultar planeta en base de datos
   - Registrar como ubicación inicial

### Sistema de Dados

**Crítico entender**: Los dados pueden ser:
- **Automáticos**: El sistema genera números aleatorios
- **Manuales**: El jugador tira dados físicos y comunica resultado

El orden importa para códigos planetarios:
- Dados [4, 6, 6] → Código 466 (no 664)

---

## 🎨 Estética Visual

### Paleta de Colores
- Fondo: Negro profundo (#050505)
- Paneles: Glassmorphism con blur
- Bordes: Cyan neón (#00f3ff)
- Acentos: Verde neón (#00ff9d), Rojo neón (#ff2a6d)

### Tipografía
- **Orbitron**: Títulos, números, displays
- **Share Tech Mono**: Texto técnico, logs

### Efectos
- Grid de fondo con transparencia cyan
- Sombras neón en hover
- Transiciones suaves (300ms)
- Animaciones pulse en alertas

---

## 🔄 Método de Trabajo

**IMPORTANTE**: Trabajo iterativo basado en el libro del juego.

### Proceso:
1. **Usuario**: Describe la lógica del libro (ej: "Ahora hay que determinar X tirando 2d6...")
2. **Desarrollador**: 
   - Implementa lógica en Python (función/endpoint)
   - Adapta frontend para soportar la interacción
   - Prueba y ajusta
3. **Iterar**: Refinamos juntos

### Ejemplo Real:
```
USUARIO: "Para empezar, tiro 2d6 para el área y 2d6 para la densidad"

DESARROLLADOR: 
  ✅ Añadí campos "area" y "world_density" a GameState
  ✅ Creé DiceRoller.world_density_from_roll() con lógica 2-4/5-9/10-12
  ✅ Implementé POST /api/games/{id}/setup
  ✅ Registra en historial de eventos y dados
  ⏳ Falta UI en dashboard (siguiente)
```

---

## 🐛 Notas Técnicas Importantes

### 1. Dependencias Python
**SIEMPRE usar uv, NO pip**:
```bash
# ✅ Correcto
uv add nombre-paquete

# ❌ Incorrecto
pip install nombre-paquete
```

### 2. Base de Datos
- SQLite se crea automáticamente al ejecutar `import_planets.py`
- El archivo `data/spacegom.db` está en `.gitignore`
- **CRÍTICO**: En nuevo entorno, ejecutar import antes de arrancar

### 3. Partidas JSON
- Se guardan en `data/games/{game_id}/state.json`
- También en `.gitignore`
- Crear partida nueva siempre genera el directorio automáticamente

### 4. Servidor con Hot Reload
```bash
uv run uvicorn app.main:app --reload --port 8000
```
- Recarga automática al editar Python
- NO recarga templates (hay que refrescar navegador)

### 5. Lints JavaScript en HTML
- Los templates tienen muchos warnings de TypeScript
- **IGNORAR**: Son falsos positivos (JavaScript en HTML)
- No afectan funcionalidad

---

## 📝 Próximos Pasos

### Inmediato (En Progreso)
- [ ] Crear UI para Setup Inicial en dashboard
  - Sección visible solo si `setup_complete === false`
  - Botón "Iniciar Setup" → llama a `/api/games/{id}/setup`
  - Muestra resultado: Área y Densidad
  - Opción para dados manuales

### Siguiente Iteración
Usuario describirá la lógica para determinar:
- [ ] Planeta inicial (3d6 para código)
- [ ] Navegación entre planetas
- [ ] Sistema de comercio
- [ ] Eventos aleatorios
- [ ] etc.

---

## 🧪 Testing Rápido

```bash
# 1. Crear partida
curl -X POST http://localhost:8000/api/games/new \
  -F "game_name=test" -s | python3 -m json.tool

# 2. Setup inicial
curl -X POST http://localhost:8000/api/games/test/setup \
  -s | python3 -m json.tool

# 3. Verificar estado
curl http://localhost:8000/api/games/test -s | python3 -m json.tool

# 4. Buscar planeta
curl http://localhost:8000/api/planets/466 -s | python3 -m json.tool
```

---

## 📚 Recursos

- **API Docs Interactive**: http://localhost:8000/docs (FastAPI automático)
- **Redoc**: http://localhost:8000/redoc
- **API.md**: Documentación de endpoints
- **README.md**: Guía de uso general

---

## 🎯 Decisiones de Diseño Clave

1. **JSON vs Base de Datos para Partidas**: JSON elegido por simplicidad y portabilidad
2. **SQLite para Planetas**: Óptimo para consultas rápidas, no cambia frecuentemente
3. **TailwindCSS CDN**: Evita compilación, más rápido para prototipar
4. **HTMX**: Interactividad sin framework pesado, ideal para MVP
5. **Dados Manuales**: Requisito crítico del usuario, preserva experiencia física

---

## 💬 Estilo de Comunicación

Cuando el usuario describe mecánicas:
- No pedir confirmación excesiva
- Implementar directamente si es claro
- Probar before mostrar
- Resumir cambios de forma concisa
- Usar emojis y markdown para claridad

Respuestas tipo:
```
✅ Implementado: [descripción breve]
📝 Estado guardado en: game_state["campo"]
🎲 Endpoint: POST /api/...
⏳ Siguiente: [lo que falta]
```

---

## 🔐 Git

```bash
# Sincronizar
git pull
git add .
git commit -m "mensaje descriptivo"
git push
```

**Archivos importantes en .gitignore**:
- `data/` (base de datos y partidas)
- `.venv/` (entorno virtual)
- `__pycache__/`

---

## 🆘 Troubleshooting

### Error: "Module not found" o problemas de importación
**Solución**: Activar el entorno virtual explícitamente.
```bash
source .venv/bin/activate
uv sync
```

### Error: "Planet X not found"
```bash
uv run python app/import_planets.py  # Re-importar planetas
```

### Puerto 8000 ocupado
```bash
lsof -ti:8000 | xargs kill  # Matar proceso
# O usar otro puerto:
uv run uvicorn app.main:app --reload --port 8001
```

### Base de datos corrupta
```bash
rm data/spacegom.db
uv run python app/import_planets.py
```

---

## 🎮 Estado del Juego

**Última mecánica implementada**: Emplazamiento Inicial
- 2d6 para Área (2-12)
- 2d6 para Densidad (Baja/Media/Alta)

**Esperando del usuario**: Siguiente lógica del juego según el libro

---

**¡Buena suerte, otro yo! 🚀**

_Última actualización: 2026-01-07_
