# SPACEGOM-WEB - Contexto Actualizado (2026-01-08)

## 📝 Resumen Ejecutivo

Aplicación web para gestionar partidas del juego de mesa **Spacegom**, desarrollada con FastAPI y persistencia en JSON + SQLite. Estado actual: **Sistema de Personal y Tesorería completamente implementado y funcional**.

---

## 🎯 Estado del Proyecto

### ✅ Implementado y Funcional

1. **Setup Inicial Completo**
   - Identidad de compañía y nave (con sugerencias automáticas de 470 nombres megacorp y 500 nombres de naves)
   - Generación de área espacial (2d6)
   - Selección de densidad de mundos
   - Búsqueda de planeta inicial válido
   - **NUEVO**: Selección de dificultad (Fácil/Normal/Difícil)
   - **NUEVO**: Creación automática de 11 empleados iniciales

2. **Dashboard Principal**
   - HUD con indicadores: Combustible, Almacén, Daños, Mes, Reputación
   - **NUEVO**: Tesorería (saldo en SC)
   - **NUEVO**: Gastos mensuales (salarios)
   - Vista de cuadrante 6x6 (Columnas A-F, Filas 1-6)
   - Sistema de exploración y descubrimiento de planetas
   - Navegación entre áreas
   - Gestión de ubicación en planeta (Mundo/Espaciopuerto/Instalación/Estación)
   - Información detallada de planetas
   - **NUEVO**: Botones de navegación a Personal y Tesorería

3. **Sistema de Personal** (/personnel)
   - Lista completa de empleados activos
   - Contratar nuevo personal (formulario completo)
   - Despedir empleados (marca como inactivo)
   - Resumen: Total empleados, Salarios totales
   - Campos: Nombre, Puesto, Salario, Experiencia (N/E/V), Moral (B/M/A), Notas

4. **Sistema de Tesorería** (/treasury)
   - Visualización de saldo actual
   - Registro de transacciones (ingresos/gastos)
   - Historial completo de transacciones
   - Categorías: Comercio, Misión, Suministros, Reparaciones, Combustible, Salarios, Préstamos
   - Resumen de gastos mensuales

5. **Base de Datos**
   - 216 planetas (códigos 3d6) con esquema refactorizado
   - Tabla `personnel` para gestión de empleados
   - Game state en JSON con difficulty, treasury, reputation, transactions

---

## 🗄️ Estructura de Base de Datos

### Tabla `planets` (216 registros)
- **Identificación**: code, name, is_custom
- **Soporte Vital**: life_support, local_contagion_risk, days_to_hyperspace, legal_order_threshold
- **Espaciopuerto**: spaceport_quality, fuel_density, docking_price
- **Instalaciones Orbitales**: 4 campos booleanos (CC, PI, DS, AA)
- **Productos**: 13 campos booleanos (INDU, BASI, ALIM, etc.)
- **Comercial**: self_sufficiency_level, ucn_per_order, max_passengers, mission_threshold
- **Validación**: tech_level, population_over_1000, convenio_spacegom
- **Notas**: notes (editable por usuario)

### Tabla `personnel` (NUEVA)
- **Campos**: id, game_id, position, name, monthly_salary, experience, morale, hire_date, is_active, notes
- **Personal inicial**: 11 empleados creados automáticamente (76 SC/mes total)

### Game State (JSON)
```json
{
  "difficulty": "normal",  // easy/normal/hard
  "treasury": 500,         // Saldo en SC
  "reputation": 0,
  "transactions": [...],
  "fuel": 18,
  "storage": 0,
  "month": 1,
  "current_planet_code": 123,
  "discovered_planets": {...},
  "quadrant_planets": {...}
}
```

---

## 🔌 API Endpoints

### Gestión de Juegos
- `POST /api/games/new` - Crear nueva partida
- `GET /api/games` - Listar partidas
- `GET /api/games/{id}` - Obtener estado de partida
- `POST /api/games/{id}/company-setup` - Guardar identidad
- `POST /api/games/{id}/area-density` - Guardar área y densidad
- `POST /api/games/{id}/set-starting-planet` - Establecer planeta inicial
- `POST /api/games/{id}/complete-setup` - **NUEVO** Completar setup con dificultad

### Planetas
- `GET /api/planets/{code}` - Información detallada
- `POST /api/games/{id}/roll-planet-code` - Generar código aleatorio
- `GET /api/planets/next/{code}` - Siguiente planeta en secuencia
- `POST /api/planets/{code}/update-notes` - Actualizar notas

### Personal (NUEVO)
- `GET /api/games/{id}/personnel` - Listar empleados
- `POST /api/games/{id}/personnel` - Contratar
- `PUT /api/games/{id}/personnel/{emp_id}` - Editar
- `DELETE /api/games/{id}/personnel/{emp_id}` - Despedir

### Tesorería (NUEVO)
- `GET /api/games/{id}/treasury` - Estado completo
- `POST /api/games/{id}/treasury/transaction` - Registrar transacción

### Sugerencias de Nombres
- `GET /api/suggestions/company-name` - Nombre de megacorporación
- `GET /api/suggestions/ship-name` - Nombre de nave

### Exploración
- `POST /api/games/{id}/explore` - Marcar cuadrante como explorado

---

## 📂 Estructura del Proyecto

```
spacegom-web/
├── app/
│   ├── main.py                  # FastAPI app + endpoints
│   ├── database.py              # Modelos SQLAlchemy (Planet, Personnel)
│   ├── game_state.py            # Gestión de estado JSON
│   ├── dice.py                  # Sistema de dados
│   ├── name_suggestions.py      # Carga de nombres desde CSV
│   ├── import_planets.py        # Importación desde Excel
│   └── templates/
│       ├── index.html           # Landing page
│       ├── setup.html           # Flujo de configuración inicial
│       ├── dashboard.html       # Panel principal
│       ├── personnel.html       # NUEVO - Gestión de personal
│       └── treasury.html        # NUEVO - Gestión de tesorería
├── data/
│   ├── spacegom.db              # SQLite (planets + personnel)
│   ├── Base_de_datos_de_planetas_simple.xlsx
│   └── games/{game_id}/state.json
├── files/                       # Materiales de referencia + CSV
│   ├── Calendario_de_Campana.pdf
│   ├── Ficha_de_Compania.pdf
│   ├── Hoja_de_Mundos.pdf
│   ├── Tesoreria.pdf
│   ├── nombres_megacorp.csv     # 470 nombres
│   ├── nombres_naves.csv        # 500 nombres
│   └── nombres_personal.csv     # 1000 nombres (futuro)
├── DATABASE.md                  # Documentación de BD
├── API.md                       # Documentación de API
├── CONTEXT.md                   # Este archivo
└── README.md
```

---

## 🎮 Flujo de Usuario

### 1. Nueva Partida (/setup)
```
Paso 1: Identidad
  → Nombre compañía (autosugestión)
  → Nombre nave (autosugestión)
  → Modelo nave

Paso 2: Área y Densidad
  → Rodar 2d6 para área (2-12)
  → Seleccionar densidad (Baja/Media/Alta)

Paso 3: Planeta Inicial
  → Generar código 3d6
  → Validar requisitos
  → Si válido: continuar. Si no: siguiente código

Paso 4: Dificultad (NUEVO)
  → Fácil: 600 SC
  → Normal: 500 SC
  → Difícil: 400 SC
  → Crea 11 empleados automáticamente
  → Redirige a dashboard
```

### 2. Dashboard (/dashboard?game_id=X)
```
HUD (Columna izquierda):
  - Combustible: 18/30
  - Almacén: 0/40 UCN
  - Daños: Leve/Moderado/Severo
  - Mes: 1/12
  - Reputación: 0 (-5 a +5)
  - Tesorería: 500 SC
  - Gastos/Mes: 76 SC

Navegación Rápida:
  - [👥 PERSONAL] → /personnel
  - [💰 TESORERÍA] → /treasury

Vista de Cuadrante:
  - Grid 6x6 (A-F, 1-6)
  - Explorar cuadrantes
  - Ver planetas descubiertos

Información de Planeta:
  - Detalles completos
  - Productos disponibles
  - Instalaciones orbitales
```

### 3. Personal (/personnel?game_id=X)
```
Resumen:
  - Total Personal: 11
  - Salarios Mensuales: 76 SC
  - Moral Promedio: Media

Acciones:
  - [+ CONTRATAR PERSONAL]
  - Ver tabla de empleados
  - Despedir empleados

Formulario de Contratación:
  - Nombre, Puesto, Salario
  - Experiencia (N/E/V)
  - Moral (B/M/A)
  - Notas
```

### 4. Tesorería (/treasury?game_id=X)
```
Resumen:
  - Saldo Actual: 500 SC
  - Salarios/Mes: 76 SC
  - Préstamos/Mes: 0 SC
  - Dificultad: Normal

Registrar Transacción:
  - Monto (+/-)
  - Categoría
  - Descripción

Historial:
  - Últimas 10 transacciones
  - Fecha, Descripción, Categoría, Monto
```

---

## 🔧 Decisiones de Diseño Importantes

### 1. Personal Inicial (11 empleados)
**Por qué**: El manual del juego establece que comienzas con el personal que trabajaba con tu madre.

**Implementación**:
- Definidos en `database.py` como `INITIAL_PERSONNEL`
- Creados automáticamente al completar setup
- Total: 76 SC/mes en salarios

### 2. Dificultad Variable
**Por qué**: Añade rejugabilidad y ajusta la dificultad inicial.

**Implementación**:
- Fácil: 600 SC (más margen de error)
- Normal: 500 SC (equilibrado)
- Difícil: 400 SC (desafío mayor)

### 3. Navegación Integrada
**Por qué**: Mejor UX, evita escribir URLs manualmente.

**Implementación**:
- Botones grandes con emojis en dashboard
- JavaScript configura `game_id` automáticamente
- Botón "Volver al Dashboard" en todas las páginas

### 4. Esquema de BD Refactorizado
**Por qué**: El esquema original tenía campos ambiguos (`life_support_1/2`, `spaceport` como string).

**Cambios**:
- `spaceport` → `spaceport_quality`, `fuel_density`, `docking_price`
- `orbital_facilities` (CSV) → 4 campos booleanos
- `life_support_1/2` → `life_support` (tipo único)

---

## 🚀 Próximos Pasos Sugeridos

### Corto Plazo
1. **Sistema de Comercio**
   - Compra/venta de productos
   - Cálculo de precios según oferta/demanda
   - Gestión de carga en el almacén

2. **Sistema de Misiones**
   - Generar misiones aleatorias
   - Tracking de progreso
   - Recompensas

3. **Navegación Mejorada**
   - Cálculo de rutas entre planetas
   - Consumo de combustible
   - Tiempo de viaje

### Medio Plazo
4. **Sistema de Eventos**
   - Eventos aleatorios durante viaje
   - Eventos de puerto espacial
   - Consecuencias de decisiones

5. **Sistema de Mejoras**
   - Upgrades de nave
   - Equipamiento especial
   - Instalaciones personalizadas

6. **Gestión Avanzada de Personal**
   - Sistema de habilidades
   - Progresión de experiencia
   - Eventos de moral

### Largo Plazo
7. **Multijugador (opcional)**
   - Compartir partidas
   - Competencia/Cooperación

8. **Estadísticas y Reportes**
   - Gráficos de progreso
   - Historial de decisiones
   - Achievements

---

## 📚 Archivos de Documentación

- **[DATABASE.md](DATABASE.md)**: Esquema completo de todas las tablas
- **[API.md](API.md)**: Documentación de todos los endpoints (pendiente actualizar con nuevos endpoints)
- **[README.md](README.md)**: Instalación, características, estructura
- **[CONTEXT.md](CONTEXT.md)**: Este archivo

---

## ⚠️ Puntos de Atención

### Para la Próxima Sesión

1. **API.md desactualizado**
   - Faltan endpoints de personnel y treasury
   - Falta endpoint de complete-setup

2. **Sistema de Préstamos**
   - Mencionado en tesorería pero no implementado
   - Considerar si implementar o remover referencias

3. **CSV nombres_personal.csv**
   - Existe (1000 nombres) pero no se usa aún
   - Podría usarse para generar nombres aleatorios al contratar

4. **Validación de Formularios**
   - Actualmente básica (required HTML)
   - Considerar validaciones más robustas

5. **Testing**
   - No hay tests automatizados
   - Toda la validación es manual

---

## 🎨 Stack Tecnológico

- **Backend**: FastAPI (Python 3.12+)
- **Base de Datos**: SQLite + SQLAlchemy
- **Persistencia**: JSON para game_state
- **Frontend**: HTML + Vanilla JavaScript + CSS (Tailwind-like classes)
- **Fuentes**: Google Fonts (Orbitron, Rajdhani)

---

## 💡 Comandos Útiles

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --reload

# Reimportar planetas
rm data/spacegom.db && python -m app.import_planets

# Ver esquema de BD
sqlite3 data/spacegom.db ".schema"

# Listar personal de un juego
sqlite3 data/spacegom.db "SELECT * FROM personnel WHERE game_id='test';"
```

---

**Última actualización**: 2026-01-08 16:10  
**Versión**: 2.0  
**Estado**: Funcional y probado ✅  
**Autor**: Desarrollo colaborativo con Gemini
