# Prompt de Continuación: Sistema de Contratación de Personal y Gestión Temporal

## Contexto del Proyecto

**Spacegom Web Companion** es una aplicación web para gestionar partidas del juego de mesa Spacegom. Estamos en la fase de implementar el **primer objetivo de la campaña**: contratar 6 tipos de personal específico.

### Stack Tecnológico

- **Backend**: FastAPI + Python 3.12
- **Base de Datos**: SQLite con SQLAlchemy
- **Frontend**: Jinja2 templates + HTMX + TailwindCSS
- **Gestión de paquetes**: `uv` y `pyenv`
- **Ruta del proyecto**: `/home/rcruz63/desarrollo/spacegom-web`

### Arquitectura Actual

```
/home/rcruz63/desarrollo/spacegom-web/
├── app/
│   ├── main.py              # FastAPI app y rutas
│   ├── database.py          # Modelos SQLAlchemy (Planet, Personnel)
│   ├── game_state.py        # Gestión de estado del juego (JSON)
│   ├── dice.py              # Sistema de dados (manual/automático)
│   ├── name_suggestions.py  # Generador de nombres aleatorios
│   ├── ship_data.py         # Datos de naves
│   └── templates/           # Templates Jinja2
├── data/
│   ├── spacegom.db         # Base de datos SQLite
│   └── games/              # Estados de partidas (JSON)
└── files/                  # Documentación del juego
```

## Estado Actual de la Implementación

### ✅ Ya Implementado

1. **Sistema de Reputación**
   - Campo `reputation` en el estado del juego (valor inicial: 0)
   - Rango: -5 a +5 (según documentación)

2. **Tabla de Personal (Personnel)**
   ```python
   - id: int (PK)
   - game_id: str (FK al juego)
   - position: str (puesto de trabajo)
   - name: str (nombre completo)
   - monthly_salary: int (salario en SC)
   - experience: str (N=Novato, E=Estándar, V=Veterano)
   - morale: str (B=Baja, M=Media, A=Alta)
   - hire_date: str
   - is_active: bool
   - notes: str
   ```

3. **Personal Inicial**
   - 11 empleados creados automáticamente al completar setup
   - Director Gerente: Widaker Farq (Veterano, Moral Alta, 20 SC)

4. **Sistema de Tesorería**
   - Campo `treasury` en el estado (en SC - Créditos Spacegom)
   - Redondeo: siempre al alza, sin decimales

5. **Sistema de Dados**
   - Archivo `dice.py` con modo automático y manual
   - Registro de tiradas en el historial

6. **Sistema de Nombres**
   - Generador de nombres aleatorios implementado
   - Usado para sugerencias de empleados

### ⚠️ Necesita Ajustes

1. **Nomenclatura de Experiencia**
   - Actualmente usa "E" para "Experto"
   - Debe cambiar a "E" para "Estándar" (según documento)

2. **Sistema de Calendario**
   - Actualmente solo hay campo `month` (mes)
   - Falta: año, día (1-35), sistema completo de fechas

## Objetivo del Siguiente Paso

Implementar el **sistema completo de contratación de personal** según el documento [`primer_objetivo.md`](file:///home/rcruz63/desarrollo/spacegom-web/primer_objetivo.md), que incluye:

### Primer Objetivo de Campaña
Contratar 6 tipos de personal:
1. Responsable de soporte a pasajeros
2. Auxiliar de vuelo
3. Negociador de compraventa de mercadería
4. Técnico de mantenimiento de astronaves
5. Técnico de soportes vitales
6. Abogado

## Sistemas a Implementar

### 1. Sistema de Calendario y Gestión Temporal

**Especificaciones:**
- Calendario: Año/Mes/Día
- Meses: 12 meses por año
- Días: 35 días por mes
- Inicio del juego: 1/1/1 (año 1, mes 1, día 1)

**Funcionalidades:**
- Sistema de **cola de eventos ordenados por fecha**
- Avance automático de tiempo hasta el próximo evento
- Eventos actuales:
  - Finalización de búsqueda de personal
  - Día 35 de cada mes (pago de salarios)

**Cambios en el estado del juego:**
```python
# Añadir a game_state.py
"year": 1,
"month": 1,
"day": 1,
"event_queue": [],  # Cola ordenada de eventos por fecha
```

### 2. Sistema de Misiones

**Dos tipos de misiones:**

**A) Objetivos de Campaña:**
```python
- numero_objetivo: int
- mundo_origen: str (código del planeta)
- lugar_ejecucion: str
- fecha_maxima: str (formato: YYYY-MM-DD)
- resultado: str ("exito" | "fracaso" | "")
```

**B) Misiones Especiales:**
```python
- codigo_mision: str
- pagina_libro: int
- mundo_origen: str
- lugar_ejecucion: str
- fecha_maxima: str
- resultado: str ("exito" | "fracaso" | "")
```

**Implementación:**
- Nueva tabla en `database.py` o almacenamiento en `game_state`
- UI para visualizar misiones activas

### 3. Catálogo de Puestos de Trabajo

**Estructura de datos necesaria:**

```python
POSITIONS_CATALOG = {
    "Abogado": {
        "tech_level_required": "RUDIMENTARIO",  # Mínimo nivel tecnológico
        "min_population": 1000,
        "search_time_dice": "1D6",  # Dados para tiempo de búsqueda
        "base_salary": 5,           # SC
        "hire_threshold": "8+",     # Objetivo en tirada 2d6
    },
    "Auxiliar de vuelo": {
        "tech_level_required": "RUDIMENTARIO",
        "min_population": 1000,
        "search_time_dice": "1",    # 1 día fijo
        "base_salary": 2,
        "hire_threshold": "7+",
    },
    # ... resto de puestos (ver primer_objetivo.md líneas 39-68)
}
```

**Niveles tecnológicos (3 categorías):**
1. Mundo > 1000 hab. y nivel RUDIMENTARIO
2. Mundo > 1000 hab. y nivel ESPACIAL (incluye anteriores)
3. Mundo > 1000 hab. y nivel INT./POL./N.SUP. (incluye anteriores)

### 4. Proceso de Contratación de Personal

#### 4.1 Mecánica de Modificadores (Reglas Universales)

**Modificadores de Experiencia:**
- Novato: -1
- Estándar: +0
- Veterano: +1

**Modificadores de Moral:**
- Baja: -1
- Media: +0
- Alta: +1

**Modificador de Reputación:**
- Se suma directamente el valor de reputación de la empresa (-5 a +5)

**Modificador Total = Experiencia + Moral + Reputación**

#### 4.2 Flujo de Contratación

**Paso 1: Inicio de Búsqueda**
- UI para seleccionar:
  - Puesto a contratar (según disponibilidad en planeta actual)
  - Nivel de experiencia deseado: Novato / Estándar / Veterano
- Verificación:
  - El Director Gerente debe estar libre (no buscando ya)
  - Estar en un Mundo (no en espacio)
  - Mundo cumple requisitos de población y nivel tecnológico

**Paso 2: Cálculo de Tiempo de Búsqueda**

```python
# Pseudocódigo
tiempo_base = tirar_dados(search_time_dice)  # Ej: 1D6, 2D6, 3D6

if nivel_candidato == "Novato":
    dias_busqueda = ceil(tiempo_base / 2)  # Redondeo al alza, mínimo 1
elif nivel_candidato == "Estándar":
    dias_busqueda = tiempo_base
elif nivel_candidato == "Veterano":
    dias_busqueda = tiempo_base * 2
```

**Paso 3: Creación de Evento de Finalización**
- Calcular fecha_fin = fecha_actual + dias_busqueda
- Añadir evento a la cola: `{"tipo": "fin_busqueda", "fecha": fecha_fin, "datos": {...}}`

**Paso 4: Avance de Tiempo**
- El tiempo salta automáticamente hasta el próximo evento:
  - Si próximo evento es "fin_busqueda" → resolver contratación
  - Si próximo evento es "pago_salarios" (día 35) → procesar salarios primero

**Paso 5: Resolución de Contratación**
- **Tirada**: 2D6 (modo manual o automático)
- **Modificadores**: 
  ```
  modificador_total = experiencia_director + moral_director + reputacion_empresa
  resultado_final = suma_dados + modificador_total
  ```
- **Éxito**: `resultado_final >= objetivo_puesto`
  - Contratar al candidato
  - Registrar en tabla Personnel
  - Calcular salario según nivel
  - Incrementar total de salarios mensuales
  - Generar nombre (aleatorio o manual)
  - Moral inicial: Media
- **Fallo**: 
  - Tiempo perdido
  - Permitir nueva búsqueda (mismo puesto u otro)

**Paso 6: Cálculo de Salario del Candidato**

```python
if nivel_candidato == "Novato":
    salario_final = ceil(base_salary / 2)  # Mitad redondeando al alza
elif nivel_candidato == "Estándar":
    salario_final = base_salary
elif nivel_candidato == "Veterano":
    salario_final = base_salary * 2
```

#### 4.3 Evolución de Personal (Aplicable en TODAS las tiradas 2d6)

**Después de cada tirada 2d6 de cualquier trabajador:**

1. **Incremento de Moral:**
   - Si `resultado_total >= 10` → Moral sube 1 nivel
   - Si `resultado_total <= 4` → Moral baja 1 nivel
   - No puede superar máximo (Alta) ni mínimo (Baja)

2. **Incremento de Experiencia:**
   - Si saca **doble 6** (independiente de modificadores) → Experiencia sube 1 nivel
   - La experiencia nunca baja
   - No puede superar Veterano

### 5. Sistema de Pago de Salarios (Día 35)

**Evento automático mensual:**

```python
# Cada día 35 del mes:
1. Calcular total_salarios = sum(salario de todos los empleados activos)
2. treasury -= total_salarios
3. Registrar transacción en historial
4. Verificar quiebra:
   if treasury < 0:
       # GAME OVER - Quiebra
       # (a menos que haya préstamos, implementar más adelante)
5. Avanzar al día 1 del siguiente mes (o mes 1 del siguiente año)
```

**IMPORTANTE:** Los nuevos empleados contratados en el mes cobran salario completo el día 35, aunque hayan sido contratados el día 34.

### 6. Componente de Dados Reusable

**Requisitos de UI:**
- Modo **automático**: botón "Tirar automáticamente" → muestra resultado
- Modo **manual**: inputs para cada dado → jugador introduce valores
- Display claro de:
  - Dados individuales (ej: [3] [5])
  - Suma total
  - Modificadores aplicados
  - Resultado final
- **Sin animaciones** (para evitar fatiga)
- Reutilizable en múltiples contextos:
  - Contratación
  - Búsqueda de planetas
  - Combate (futuro)
  - Etc.

**Componente sugerido:**
```html
<!-- Componente HTMX + Jinja2 -->
<div class="dice-roller">
    <div class="dice-mode-selector">
        <button>Automático</button>
        <button>Manual</button>
    </div>
    
    <!-- Modo automático -->
    <button hx-post="/roll-dice" hx-target="#dice-result">
        🎲 Tirar XdY
    </button>
    
    <!-- Modo manual -->
    <div class="manual-inputs">
        <input type="number" min="1" max="6" placeholder="Dado 1">
        <input type="number" min="1" max="6" placeholder="Dado 2">
        <button>Confirmar</button>
    </div>
    
    <!-- Resultado -->
    <div id="dice-result">
        <div class="dice-values">[3] [5]</div>
        <div class="dice-sum">Suma: 8</div>
        <div class="modifiers">Modificadores: +2</div>
        <div class="total">Total: 10</div>
    </div>
</div>
```

### 7. Sistema de Despidos (Para Completitud)

**Dos modalidades:**

**A) Despido Inmediato (sin coste)**
- Efecto: 
  - Reputación empresa: -1
  - Moral de todos los empleados: -1
- Aplicar inmediatamente

**B) Despido Indemnizado**
- Coste: 5 mensualidades (salario_mensual × 5)
- Sin penalizaciones

**Restricción durante Tutorial:**
- No se puede despedir durante el tutorial (explicado más adelante en el juego)

## Estructura de Archivos a Modificar/Crear

### Modificar

1. **`app/database.py`**
   - [ ] Ajustar `EXPERIENCE_LEVELS` ("E" → "Estándar")
   - [ ] Añadir tabla `Mission` (o decidir JSON en state)
   - [ ] Añadir diccionario `POSITIONS_CATALOG` con todos los puestos

2. **`app/game_state.py`**
   - [ ] Añadir campos de calendario: `year`, `day`
   - [ ] Añadir `event_queue` para cola de eventos
   - [ ] Métodos para gestión temporal:
     - `add_event_to_queue(event_type, date, data)`
     - `get_next_event()`
     - `advance_to_next_event()`
     - `process_event(event)`
   - [ ] Métodos para salarios:
     - `calculate_total_salaries(db)`
     - `pay_monthly_salaries(db)`
     - `check_bankruptcy()`

3. **`app/main.py`**
   - [ ] Endpoint: `POST /hire/start` - Iniciar búsqueda de personal
   - [ ] Endpoint: `POST /hire/resolve` - Resolver contratación
   - [ ] Endpoint: `GET /hire/available-positions` - Puestos disponibles en mundo actual
   - [ ] Endpoint: `POST /time/advance` - Avanzar tiempo al próximo evento
   - [ ] Endpoint: `GET /missions` - Listar misiones
   - [ ] Actualizar dashboard para mostrar calendario completo

4. **`app/dice.py`**
   - [ ] Revisar para asegurar compatibilidad con el nuevo componente UI
   - [ ] Añadir método para aplicar modificadores visualmente

### Crear Nuevos Archivos

1. **`app/templates/components/dice_roller.html`**
   - Componente reutilizable de dados

2. **`app/templates/hire_personnel.html`**
   - UI completa para contratar personal
   - Selector de puesto y nivel
   - Visualización de tiempo de búsqueda
   - Resolución de contratación

3. **`app/templates/components/calendar_widget.html`**
   - Widget para mostrar fecha actual
   - Próximo evento
   - Botón de avanzar tiempo

4. **`app/hire_logic.py`** (opcional, para separar lógica)
   - Funciones auxiliares de contratación
   - Cálculo de tiempos
   - Validaciones

## Plan de Implementación Sugerido

### Fase 1: Fundamentos Temporales (Prioridad Alta)
1. Sistema de calendario (year, month, day)
2. Cola de eventos ordenados
3. Avance de tiempo hasta próximo evento
4. Evento de pago mensual (día 35)

### Fase 2: Catálogo de Puestos (Prioridad Alta)
1. Diccionario completo de puestos
2. Validación según nivel tecnológico de planeta
3. UI para mostrar puestos disponibles

### Fase 3: Proceso de Contratación (Prioridad Alta)
1. UI de selección (puesto + nivel)
2. Cálculo de tiempo de búsqueda con dados
3. Creación de evento de finalización
4. Resolución con tirada 2d6 + modificadores
5. Registro de nuevo empleado
6. Sistema de evolución (moral/experiencia)

### Fase 4: Componente de Dados (Prioridad Media)
1. Diseño del componente reutilizable
2. Integración en proceso de contratación
3. Modo manual y automático claramente diferenciados

### Fase 5: Sistema de Misiones (Prioridad Baja)
1. Tabla o estructura de misiones
2. UI para listar misiones
3. Registro del primer objetivo

### Fase 6: Despidos (Prioridad Baja)
1. Lógica de despido inmediato
2. Lógica de despido indemnizado
3. Restricción durante tutorial

## Consideraciones Técnicas

### Formato de Fechas
```python
# Usar formato personalizado del juego
fecha_str = f"{year}-{month:02d}-{day:02d}"  # Ej: "1-01-15"

# Comparación de fechas
def compare_dates(date1_str, date2_str):
    # Convertir y comparar
    pass
```

### Cola de Eventos
```python
# Estructura sugerida
event = {
    "type": "hire_resolution | salary_payment | ...",
    "date": "1-01-15",
    "data": {
        "position": "Abogado",
        "experience_level": "Novato",
        # ... otros datos específicos
    }
}

# Ordenar por fecha
event_queue.sort(key=lambda e: parse_date(e["date"]))
```

### Redondeo de Valores
```python
import math

# SIEMPRE redondear al alza en tesorería
amount = math.ceil(value)
```

## Documentos de Referencia

- [`primer_objetivo.md`](file:///home/rcruz63/desarrollo/spacegom-web/primer_objetivo.md) - Especificación completa del objetivo
- [`API.md`](file:///home/rcruz63/desarrollo/spacegom-web/API.md) - Documentación de API actual
- [`CONTEXT_ACTUALIZADO.md`](file:///home/rcruz63/desarrollo/spacegom-web/CONTEXT_ACTUALIZADO.md) - Contexto del proyecto
- [`DATABASE.md`](file:///home/rcruz63/desarrollo/spacegom-web/DATABASE.md) - Esquema de base de datos
- `files/Calendario_de_Campana.pdf` - Calendario de campaña (reputación -5 a +5)

## Notas Finales

- **Progresividad**: El desarrollo debe ser incremental, probando cada fase antes de continuar
- **Reutilización**: El sistema de dados debe ser lo suficientemente flexible para otros usos futuros
- **Testing**: Verificar especialmente:
  - Cálculo correcto de tiempo de búsqueda (dados + ajustes por nivel)
  - Modificadores de tirada (experiencia + moral + reputación)
  - Pago de salarios en día 35
  - Detección de quiebra
  - Evolución de moral/experiencia según resultados

---

**Estado**: Listo para implementación
**Prioridad**: Alta (bloquea progreso de la campaña)
**Complejidad estimada**: Media-Alta (múltiples sistemas interdependientes)
