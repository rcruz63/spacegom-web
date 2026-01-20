# Spacegom Companion - Panel de Control Espacial

![Spacegom](https://img.shields.io/badge/Spacegom-Companion-00f3ff?style=for-the-badge)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-3D72D7?style=for-the-badge&logo=htmx&logoColor=white)

Aplicación web companion para el juego de mesa/rol **Spacegom**. Sustituye el soporte físico de papel y lápiz con un panel interactivo estilo "Spacecraft Control Panel" con estética cyberpunk/espacial.

## 🌌 Características

### ✅ Sistema Completamente Funcional

#### 🚀 Setup de Partida Completo
- **Identificación de Compañía y Nave**: Nombres personalizables con sugerencias aleatorias
- **Determinación de Área**: Tirada de 2d6 para determinar el área espacial (2-12)
- **Densidad de Mundos**: Tirada de 2d6 con clasificación automática (Baja/Media/Alta)
- **Posición Inicial**: Determinación de cuadrante inicial (grid 6x6)
- **Planeta de Origen**:
  - Tirada de 3d6 para código de planeta (111-666)
  - **Validación Automática**: Verifica requisitos de inicio (tecnología, población, convenio, soporte vital, productos)
  - **Búsqueda Consecutiva**: Si el planeta no es apto, busca el siguiente código secuencial automáticamente (111 → 112 → 113...)
  - Actualización de datos faltantes desde el mismo setup
- **Dificultad**: Tres niveles (Fácil: 600 SC, Normal: 500 SC, Difícil: 400 SC)
- **Personal Inicial**: 11 empleados creados automáticamente (76 SC/mes)

#### 🎯 HUD Superior - Estado Crítico
- **Reserva de Combustible**: Indicador visual animado (0-30 unidades)
- **Capacidad de Almacén**: Monitor de bodega de la nave (40 UCN para Basic Starfall)
- **Sistema de Daños**: Tres niveles (Leves, Moderados, Graves) con alerta crítica
- **Calendario de Campaña**: Seguimiento de meses con **35 días por mes**
- **Reputación**: Rango dinámico de **-5 a +5** con codificación por colores
- **Tesorería**: Saldo actual y gastos mensuales

#### 🗺️ Vista de Cuadrante - Navegación Espacial
- **Grid Interactivo 6x6**: Representa el área de exploración actual
- **Niebla de Guerra**: Cuadrantes sombreados hasta ser explorados
- **Marcador de Posición**: Indicador visual de la ubicación actual de la nave
- **Información Planetaria Expandida**: Panel lateral con detalles completos:
  - Soporte Vital, Nivel Tecnológico, Riesgo de Contagio
  - Espaciopuerto (Calidad, Combustible, Precio de Amarre)
  - Instalaciones Orbitales (Centro de Cartografía, Academia, etc.)
  - Productos disponibles y restricciones comerciales
  - Convenio Spacegom y autosuficiencia

#### ⚖️ Terminal de Comercio de Mercancías ⭐ NUEVO
- **Vista de OFERTA (Comprar)**: Productos disponibles filtrados por capacidad productiva planetaria
- **Vista de DEMANDA (Vender)**: Carga actual disponible para venta
- **Negociación con Dados**: Sistema 2d6 con modificadores de reputación y habilidad
- **Registro de Pedidos (Ledger)**: Historial completo de transacciones con trazabilidad
- **Lógica de Mercado**: Restricciones de venta local, cooldowns de producción
- **Precios Dinámicos**: Multiplicadores (0.8x, 1.0x, 1.2x) basados en negociación

#### ✈️ Transporte de Pasajeros ⭐ NUEVO
- **Widget en Dashboard**: Visible solo en superficie planetaria
- **Cálculo Automático**: Capacidad vs demanda con modificadores de auxiliares
- **Tiradas de Dados**: Determinación de afluencia con impacto en moral/experiencia
- **Ingresos Dinámicos**: Basados en pasajeros transportados y bonos de experiencia

#### 👥 Gestión de Personal Avanzada
- **Sistema de Empleados**: 11 empleados iniciales con datos completos
- **Contratación Automatizada**: Modal con 29 puestos filtrados por nivel tecnológico
- **Cola de Tareas del Director**: Gestión ordenada de búsquedas de personal
- **Avance Temporal**: Resolución automática de eventos con tiradas y modificadores
- **Moral y Experiencia**: Evolución automática basada en reglas del juego
- **Salarios Dinámicos**: Ajustes por nivel de experiencia

#### 💰 Sistema de Tesorería Completo
- **Saldo Actual**: Créditos Spacegom (SC) con seguimiento en tiempo real
- **Registro de Transacciones**: Manual con categorías (Comercio, Misión, Suministros, etc.)
- **Historial Detallado**: Fechas, descripciones, montos con codificación visual
- **Gastos Mensuales**: Salarios automáticos + préstamos

#### 🎯 Gestión de Misiones y Eventos
- **Objetivos de Campaña**: Seguimiento de objetivos principales
- **Misiones Especiales**: Gestión de misiones del libro (código y página)
- **Sistema Temporal**: Cola de eventos con resolución automática
- **Fechas Límite**: Eventos automáticos en el calendario

#### 📜 Sistema de Logging
- **Eventos del Juego**: Registro automático de todas las acciones
- **Fechas Duales**: Timestamp del juego + timestamp real
- **Categorización**: Info, Success, Warning, Error
- **Historial Persistente**: Almacenado en estado del juego

### 🎨 Estética Visual Cyberpunk

- **Paleta de Colores**: Dark mode con slate-950 como base
- **Bordes Neón**: Cyan (#00f3ff) y verde neón (#00ff9d)
- **Tipografía Técnica**:
  - `Orbitron`: Títulos y displays numéricos
  - `Share Tech Mono`: Texto técnico y monoespaciado
- **Efectos Visuales**:
  - Glassmorphism para paneles
  - Gradientes dinámicos
  - Animaciones suaves en interacciones
  - Background grid de estilo terminal espacial
  - Efectos de niebla de guerra
  - Indicadores visuales de daño y estado

## 🚀 Tecnologías

- **Backend**: FastAPI (Python 3.12+) con SQLAlchemy ORM
- **Frontend**: HTML + TailwindCSS + HTMX + JavaScript vanilla
- **Base de Datos**: SQLite con 216 planetas importados + tablas dinámicas
- **Persistencia**: JSON para estado del juego + SQLite para datos relacionales
- **Fonts**: Orbitron, Share Tech Mono (Google Fonts)
- **Interactividad**: JavaScript vanilla + HTMX para actualizaciones dinámicas
- **Package Manager**: uv para gestión de dependencias
- **Arquitectura**: Modular con separación clara backend/frontend

## 📦 Instalación y Uso

### Requisitos Previos
- Python 3.12+
- uv (gestor de paquetes): `pip install uv`

### Instalación

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd spacegom-web

# Instalar dependencias con uv
uv sync
```

### Ejecutar la Aplicación

```bash
# Opción 1: Usando uvicorn directamente
source .venv/bin/activate
uvicorn main:app --app-dir app --reload --port 8000

# Opción 2: Scripting con uv
uv run uvicorn main:app --app-dir app --reload
```

La aplicación estará disponible en: `http://localhost:8000`

### Acceder a la Aplicación

1. **Página principal**: `http://localhost:8000/`
2. **Nueva Partida**: `http://localhost:8000/setup`
3. **Panel de Control**: `http://localhost:8000/dashboard?game_id=X`
4. **Personal**: `http://localhost:8000/personnel?game_id=X`
5. **Comercio**: `http://localhost:8000/trade?game_id=X`
6. **Tesorería**: `http://localhost:8000/treasury?game_id=X`
7. **Misiones**: `http://localhost:8000/missions?game_id=X`

## 🎮 Uso del Panel de Control

### Setup Inicial
1. **Identificación**: Introduce los nombres de tu compañía y nave (o usa las sugerencias automáticas)
2. **Área y Densidad**: El sistema tira automáticamente 2d6 para determinar el área y densidad
3. **Posición**: Se determina tu cuadrante inicial en el grid 6x6
4. **Planeta**: Tira 3d6 para tu planeta de origen
   - Si no es apto, el sistema buscará automáticamente el siguiente código válido
   - Completa datos faltantes si es necesario
5. **Dificultad**: Elige entre Fácil (600 SC), Normal (500 SC) o Difícil (400 SC)
   - Se crean automáticamente 11 empleados iniciales (76 SC/mes)
6. **Finalizar**: Accede al dashboard para comenzar tu aventura

### Páginas Disponibles
- **Dashboard** (`/dashboard?game_id=X`): Panel principal con HUD, navegación y cuadrante
- **Personal** (`/personnel?game_id=X`): Gestión de empleados (acceso desde botón 👥 en dashboard)
- **Tesorería** (`/treasury?game_id=X`): Finanzas y transacciones (acceso desde botón 💰 en dashboard)

### HUD Superior
- **Combustible/Almacén**: Usa los botones `+/-` para ajustar valores
- **Daños**: Haz clic en los indicadores para activar/desactivar
- **Calendario/Reputación**: Usa las flechas `◄►` para navegar

### Vista de Cuadrante
- Haz clic en cualquier cuadrante para explorarlo
- La niebla de guerra se disipa al explorar
- Los planetas muestran información detallada al seleccionarlos

### Tripulación
- Visualiza el estado de cada miembro
- Monitor de salubridad general

### Terminal Comercial
- Ajusta modificadores de precio según negociación
- Botones de COMPRAR/VENDER para transacciones
- Resumen financiero en tiempo real

## 📁 Estructura del Proyecto

```
spacegom-web/
├── 📄 pyproject.toml          # Configuración de proyecto y dependencias
├── 📄 spacegom.sh             # Script de automatización
├── 📄 README.md               # Este archivo
├── 📄 API.md                  # Documentación de endpoints API
├── 📄 DATABASE.md             # Documentación de base de datos
├── 📄 DICE_SYSTEM.md          # Sistema de dados y probabilidades
├── 📄 CONTEXT_ACTUALIZADO.md  # Contexto actual del proyecto
├── 📄 REGLAS_MORAL_EXPERIENCIA.md # Reglas de experiencia y moral
├── 📄 primer_objetivo.md      # Objetivos iniciales del proyecto
├── 📄 campaña.md              # Sistema de campaña
├── 📄 review.md               # Revisión del proyecto
├── 📄 implementacion_transporte_pasajeros.md # Transporte de pasajeros
├── 📄 accion_comercio_de_mercancias.md # Comercio de mercancías
├── 📄 fix_db.py               # Script de corrección de base de datos
├── 📁 app/                    # Código fuente principal
│   ├── 📄 __init__.py         # Inicialización del paquete
│   ├── 📄 main.py             # API FastAPI principal
│   ├── 📄 database.py         # Configuración de base de datos
│   ├── 📄 models.py           # Modelos SQLAlchemy
│   ├── 📄 game_state.py       # Gestión del estado del juego
│   ├── 📄 dice.py             # Sistema de dados
│   ├── 📄 event_handlers.py   # Manejadores de eventos
│   ├── 📄 event_logger.py     # Logger de eventos
│   ├── 📄 personnel_manager.py # Gestión de personal
│   ├── 📄 trade_manager.py    # Gestión de comercio
│   ├── 📄 time_manager.py     # Gestión del tiempo
│   ├── 📄 ship_data.py        # Datos de naves
│   ├── 📄 name_suggestions.py # Sugerencias de nombres
│   ├── 📄 import_planets.py   # Importación de planetas
│   ├── 📄 update_planets_from_excel.py # Actualización de planetas
│   ├── 📄 utils.py            # Utilidades generales
│   ├── 📄 run.py              # Script de ejecución
│   ├── 📁 static/             # Archivos estáticos
│   │   └── 📁 js/             # JavaScript del frontend
│   │       ├── 📄 dice-roller.js      # Componente de dados
│   │       └── 📄 passenger_transport.js # Transporte de pasajeros
│   └── 📁 templates/          # Plantillas HTML
│       ├── 📄 base.html       # Plantilla base
│       ├── 📄 index.html      # Página principal
│       ├── 📄 setup.html      # Configuración de partida
│       ├── 📄 dashboard.html  # Panel de control principal
│       ├── 📄 personnel.html  # Gestión de personal
│       ├── 📄 trade.html      # Comercio
│       ├── 📄 treasury.html   # Tesorería
│       ├── 📄 missions.html   # Misiones
│       ├── 📄 logs.html       # Logs de eventos
│       └── 📁 components/     # Componentes reutilizables
│           ├── 📄 dice_result.html    # Resultado de dados
│           └── 📄 dice_widget.html    # Widget de dados
├── 📁 files/                  # Archivos de datos
│   ├── 📄 nombres_megacorp.csv    # Nombres de megacorps
│   ├── 📄 nombres_naves.csv       # Nombres de naves
│   └── 📄 nombres_personal.csv     # Nombres de personal
├── 📁 docs/                   # Documentación generada
│   ├── 📄 main.md             # API principal
│   ├── 📄 database.md         # Base de datos
│   ├── 📄 models.md           # Modelos de datos
│   ├── 📄 game_state.md       # Estado del juego
│   ├── 📄 dice.md             # Sistema de dados
│   ├── 📄 event_handlers.md   # Manejadores de eventos
│   ├── 📄 personnel_manager.md # Gestión de personal
│   ├── 📄 trade_manager.md    # Comercio
│   ├── 📄 time_manager.md     # Tiempo
│   ├── 📄 ship_data.md        # Datos de naves
│   ├── 📄 name_suggestions.md # Sugerencias de nombres
│   ├── 📄 import_planets.md   # Importación de planetas
│   ├── 📄 utils.md            # Utilidades
│   ├── 📄 dice-roller.md      # Dados frontend
│   ├── 📄 passenger_transport.md # Transporte frontend
│   ├── 📄 base.html.md        # Plantilla base
│   ├── 📄 index.html.md       # Página principal
│   ├── 📄 setup.html.md       # Setup
│   ├── 📄 dashboard.html.md   # Dashboard
│   ├── 📄 personnel.html.md   # Personal
│   ├── 📄 trade.html.md       # Comercio
│   ├── 📄 treasury.html.md    # Tesorería
│   ├── 📄 missions.html.md    # Misiones
│   ├── 📄 logs.html.md        # Logs
│   ├── 📄 dice_result.html.md # Resultado dados
│   └── 📄 dice_widget.html.md # Widget dados
└── 📁 old_docs/               # Documentación antigua
    ├── 📄 CONTEXT.md
    ├── 📄 HiringEndpointsNotes.md
    ├── 📄 IMPLEMENTACION_CONTRATACION.md
    ├── 📄 migrate_preserve_planets.py
    ├── 📄 OLD_CONTEXT_ACTUALIZADO.md
    ├── 📄 OLD_Implementation.md
    └── 📄 planets_backup.json
```

## 📚 Documentación Técnica Detallada

Se ha generado documentación completa para todos los archivos fuente del proyecto en la carpeta `docs/`:

### Backend (Python)
- **[main.md](docs/main.md)**: API FastAPI completa con todos los endpoints
- **[database.md](docs/database.md)**: Configuración de base de datos y modelos SQLAlchemy
- **[models.md](docs/models.md)**: Modelos de datos adicionales y esquemas
- **[game_state.md](docs/game_state.md)**: Sistema de persistencia JSON del estado del juego
- **[state_file.md](docs/state_file.md)**: Estructura completa del archivo state.json y campos del estado del juego
- **[dice.md](docs/dice.md)**: Utilidades de dados y generación de códigos planetarios
- **[event_handlers.md](docs/event_handlers.md)**: Sistema modular de manejo de eventos
- **[personnel_manager.md](docs/personnel_manager.md)**: Gestión avanzada de empleados y contratación
- **[trade_manager.md](docs/trade_manager.md)**: Lógica de comercio y negociación
- **[time_manager.md](docs/time_manager.md)**: Gestión del calendario y tiempo de campaña
- **[ship_data.md](docs/ship_data.md)**: Modelos de naves y estadísticas
- **[name_suggestions.md](docs/name_suggestions.md)**: Generación de nombres aleatorios
- **[import_planets.md](docs/import_planets.md)**: Importación de datos planetarios
- **[utils.md](docs/utils.md)**: Utilidades generales del proyecto

### Frontend (JavaScript)
- **[dice-roller.md](docs/dice-roller.md)**: Componente universal de tiradas de dados
- **[passenger_transport.md](docs/passenger_transport.md)**: Gestión de transporte de pasajeros

### Templates (HTML)
- **[base.html.md](docs/base.html.md)**: Plantilla base con estilos y navegación
- **[index.html.md](docs/index.html.md)**: Página principal de bienvenida
- **[setup.html.md](docs/setup.html.md)**: Asistente completo de configuración de partida
- **[dashboard.html.md](docs/dashboard.html.md)**: Panel de control principal con HUD
- **[personnel.html.md](docs/personnel.html.md)**: Gestión de personal y empleados
- **[trade.html.md](docs/trade.html.md)**: Terminal comercial de mercancías
- **[treasury.html.md](docs/treasury.html.md)**: Sistema de finanzas y transacciones
- **[missions.html.md](docs/missions.html.md)**: Gestión de misiones y objetivos
- **[logs.html.md](docs/logs.html.md)**: Historial de eventos del juego
- **[dice_result.html.md](docs/dice_result.html.md)**: Componente de resultados de dados
- **[dice_widget.html.md](docs/dice_widget.html.md)**: Widget interactivo de dados

Cada archivo de documentación incluye:
- **Descripción completa**: Propósito y funcionalidad del módulo
- **Dependencias**: Librerías y módulos importados
- **Funciones/Clases**: Lista detallada con parámetros y retornos
- **Uso típico**: Ejemplos de implementación
- **Notas de implementación**: Decisiones técnicas y consideraciones

El proyecto incluye materiales originales del juego de mesa en la carpeta `files/`:

### Documentos PDF
- **Calendario de Campaña**: Sistema de 35 días por mes
- **Ficha de Compañía**: Plantilla oficial para gestión de empresa
- **Hoja de Mundos**: Listado completo de planetas con códigos 3d6
- **Tesorería**: Control financiero detallado
- **Pack Completo**: Todos los descargables del juego

### Archivos CSV de Nombres
- **nombres_megacorp.csv**: 470 nombres de megacorporaciones
- **nombres_naves.csv**: 500 nombres de naves espaciales inspirados en ficción, historia y mitología
- **nombres_personal.csv**: 1000 nombres de personal para futura gestión de tripulación

## 🔮 Próximas Mejoras

- [ ] Sistema de eventos aleatorios (diarios/de viaje)
- [ ] Sistema de combate espacial
- [ ] Calendario dinámico con meses de 35 días
- [ ] Mejora y reparación de naves en astilleros
- [ ] Sistema de misiones y contratos procedurales
- [ ] Gestión detallada de carga (peso/volumen)
- [ ] Modo multijugador
- [ ] Generación procedural de planetas adicionales
- [ ] Gráficos de estadísticas y progreso
- [ ] Exportación de partidas a PDF

## 🛠️ Desarrollo

### Agregar Nuevas Rutas

Edita `app/main.py`:

```python
@app.get("/nueva-ruta")
async def nueva_ruta(request: Request):
    return templates.TemplateResponse("tu_template.html", {"request": request})
```

### Personalizar Estilos

Los estilos base están en `app/templates/base.html`. Puedes modificar:
- Colores personalizados en las clases de Tailwind
- Estilos CSS adicionales en la sección `<style>`
- Variables de color neón

### Importar Datos de Planetas

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar script de importación
python -m app.import_planets
```

## 📖 Documentación Adicional

Para más información sobre el proyecto:

- **[API.md](API.md)**: Documentación completa de todos los endpoints de la API REST
- **[DATABASE.md](DATABASE.md)**: Esquema detallado de la base de datos, campos de la tabla `planets`, ejemplos y consultas útiles
- **[CONTEXT_ACTUALIZADO.md](CONTEXT_ACTUALIZADO.md)**: Contexto del proyecto, decisiones de diseño y próximos pasos
- **[docs/](docs/)**: Documentación técnica detallada de todos los archivos fuente (28 archivos)
- **[DICE_SYSTEM.md](DICE_SYSTEM.md)**: Sistema completo de dados y probabilidades
- **[REGLAS_MORAL_EXPERIENCIA.md](REGLAS_MORAL_EXPERIENCIA.md)**: Reglas de moral y experiencia del personal

## 📝 Licencia

[Especifica tu licencia aquí]

## 👨‍🚀 Créditos

Desarrollado para la comunidad de Spacegom.

**Mecánicas de juego** basadas en el manual oficial de Spacegom.

---

**¡Que tengas un buen viaje, Comandante!** 🚀
