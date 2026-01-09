# SPACEGOM-WEB - Contexto Actualizado (2026-01-09)

## 📝 Resumen Ejecutivo

Aplicación web para gestionar partidas del juego de mesa **Spacegom**, desarrollada con FastAPI. Estado actual: **Sistema de Personal con Contratación Automatizada + Gestión Temporal + UX Mejorado - Completamente Funcional**.

---

## 🎯 Estado del Proyecto

### ✅ Implementado y Funcional

1. **Setup Inicial Completo**
   - Identidad compañía/nave
   - Área, densidad, planeta inicial
   - Dificultad (Fácil/Normal/Difícil)
   - 11 empleados iniciales automáticos

2. **Dashboard Principal**
   - HUD: Combustible, Almacén, Daños, Mes, Reputación, Tesorería
   - Vista cuadrante 6x6 con exploración
   - Navegación a Personal/Tesorería/Misiones
   - **LIMPIO**: Eliminados componentes obsoletos (Tripulación, Terminal Comercial)

3. **Sistema de Personal** (/personnel) ⭐ NUEVO
   - **Contratación Automatizada**:
     - Modal con 29 puestos catalogados
     - Filtrado por nivel tecnológico del planeta
     - 3 niveles experiencia (Novato/Estándar/Veterano)
     - Cálculo automático tiempo/salario
   - **Cola de Tareas del Director Gerente**:
     - Vista actual + pendientes + completadas
     - Eliminar tareas pendientes
     - Auto-inicio de siguiente tarea
   - **Avance Temporal**:
     - Botón "⏩ AVANZAR TIEMPO"
     - Resolución con tiradas 2d6 + modificadores
     - Creación automática de empleados
     - Evolución de moral/experiencia del Director

4. **Sistema de Notificaciones** ⭐ NUEVO
   - **Toast Notifications** (esquina superior derecha):
     - 4 tipos: success, error, info, warning
     - Animaciones slide-in/out
   - **Panel Lateral de Resultados**:
     - Slide-in desde derecha
     - Dados visuales con colores
     - Detalles completos de contratación
     - Info de siguiente tarea auto-iniciada

5. **Sistema Temporal** (`time_manager.py` - 323 líneas) ⭐ NUEVO
   - **GameCalendar**: 35 días/mes, 12 meses/año
   - **EventQueue**: Cola ordenada de eventos
   - Funciones: `calculate_hire_time()`, `calculate_hire_salary()`

6. **Sistema de Tesorería** (/treasury)
   - Saldo, transacciones, historial
   - Categorías de gastos

7. **Sistema de Misiones** (/missions)
   - Objetivos de campaña
   - Misiones especiales
   - Estado y tracking

8. **Base de Datos**
   - 216 planetas
   - Tabla `personnel`
   - Tabla `employee_tasks` ⭐ NUEVO
   - Catálogo de 29 puestos ⭐ NUEVO

---

## 🗄️ Estructura de Base de Datos

### Tabla `employee_tasks` (NUEVA)
```python
- id, game_id, employee_id
- task_type ("hire_search")
- status (pending/in_progress/completed/failed)
- queue_position (1, 2, 3...)
- task_data (JSON): position, experience, days, salary, threshold
- result_data (JSON): dice, modifiers, success, new_employee_id
- created_date, started_date, completion_date, finished_date
```

### Catálogos Nuevos
- **POSITIONS_CATALOG**: 29 puestos x nivel tecnológico
- **TECH_LEVEL_REQUIREMENTS**: Compatibilidad planeta-puesto

### Game State (JSON) - ACTUALIZADO
```json
{
  "year": 1,
  "day": 1,
  "event_queue": [...],  // NUEVO
  "difficulty": "normal",
  "treasury": 500,
  "reputation": 0,
  "transactions": [...],
  "fuel": 18,
  "current_planet_code": 111,
  "discovered_planets": {...}
}
```

---

## 🔌 API Endpoints

### Personal y Contratación (NUEVO)
- `GET /api/games/{id}/hire/available-positions` - Puestos disponibles
- `POST /api/games/{id}/hire/start` - Iniciar búsqueda
- `GET /api/games/{id}/personnel/{emp_id}/tasks` - Cola de tareas
- `PUT /api/games/{id}/tasks/{task_id}/reorder` - Reordenar cola
- `DELETE /api/games/{id}/tasks/{task_id}` - Eliminar tarea
- `POST /api/games/{id}/time/advance` ⭐ - Avanzar tiempo

### Misiones (NUEVO)
- `GET /api/games/{id}/missions` - Listar misiones
- `POST /api/games/{id}/missions` - Crear misión
- `PUT /api/games/{id}/missions/{mission_id}` - Actualizar
- `DELETE /api/games/{id}/missions/{mission_id}` - Eliminar

### (resto de endpoints anteriores...)

---

## 📂 Estructura del Proyecto

```
spacegom-web/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── game_state.py
│   ├── time_manager.py        # NUEVO - 323 líneas
│   ├── dice.py
│   ├── name_suggestions.py
│   └── templates/
│       ├── base.html          # ACTUALIZADO - Sistema notificaciones
│       ├── dashboard.html     # LIMPIADO - 273 líneas eliminadas
│       ├── personnel.html     # REESCRITO - Sistema contratación
│       ├── treasury.html
│       └── missions.html      # NUEVO
├── data/
│   ├── spacegom.db
│   └── games/{game_id}/state.json
└── files/
```

---

## 🎮 Flujo de Usuario - Sistema de Contratación

```
1. Usuario va a /personnel?game_id=X

2. Click "+ INICIAR BÚSQUEDA"
   → Modal se abre
   → Selecciona puesto (filtrado por tech_level planeta)
   → Elige experiencia (Novato/Estándar/Veterano)
   → Ve resumen: días estimados, salario final
   → Click "Iniciar Búsqueda"

3. Toast verde: "Búsqueda iniciada - Cola #1"
   → Tarea aparece en cola como "EN PROCESO"

4. Click "⏩ AVANZAR TIEMPO"
   → Confirm dialog
   → Toast azul: "Tiempo avanzado: 1-01-01 → 1-01-02"
   → Panel lateral desliza desde derecha:
      • Dados visuales [5] + [6] = 11
      • Modificadores +2
      • Resultado: 13 vs Umbral: 8
      • ✅ ÉXITO - Empleado contratado
      • Siguiente tarea auto-iniciada

5. Tabla actualizada con nuevo empleado
   → Cola actualizada (siguiente tarea "EN PROCESO")
```

---

## 🔧 Decisiones de Diseño Nuevas

### 1. Cola de Tareas del Director
**Por qué**: El manual establece que el Director Gerente gestiona las contrataciones.

**Implementación**:
- Una tarea activa a la vez (`status: "in_progress"`)
- Tareas pendientes en cola ordenada (`queue_position`)
- Auto-inicio de siguiente tarea al completar actual

### 2. Sistema Temporal con Eventos
**Por qué**: Necesario para gestionar múltiples tareas futuras.

**Implementación**:
- `event_queue` en game_state
- Eventos con tipo, fecha y datos
- Procesamiento ordenado por fecha

### 3. Sistema de Notificaciones Integrado
**Por qué**: Los `alert()` del navegador son feos y bloquean la UI.

**Implementación**:
- Toast notifications no-bloqueantes
- Panel lateral para resultados detallados
- Funciones globales en `base.html`

### 4. Dashboard Limpiado
**Por qué**: Componentes "Tripulación" y "Terminal Comercial" eran prototipos obsoletos.

**Cambios**:
- Eliminadas 273 líneas de código
- Dashboard enfocado en Vista Cuadrante + HUD
- Uso de /personnel y /treasury en su lugar

---

## 🚀 Próximos Pasos

### Alta Prioridad
1. **Navegación Entre Áreas**
   - Selector de área explorada
   - Persistencia de datos por área
   - Switch entre cuadrantes

2. **Pantalla de Selección de Partidas**
   - Landing page con grid de partidas
   - Botones: Continuar, Borrar, Nueva
   - Metadata visible

### Media Prioridad
3. **Mejoras UX**
   - Fix fondo estrellado (canvas estrellas)
   - employee_number por compañía
   - Reordenar cola con drag & drop

### Implementaciones Futuras
4. **Sistema de Comercio Completo**
5. **Eventos Aleatorios**
6. **Mejoras de Nave**

---

## ⚠️ Puntos de Atención

### Bugs Conocidos
- Ninguno crítico identificado

### Limitaciones Actuales
- No se puede reordenar cola visualmente (endpoint existe, UI pendiente)
- Fondo estrellado no visible
- Sin pantalla de selección de partidas (dificulta gestión multi-juego)
- Sin navegación entre áreas (bloqueante para exploración avanzada)

### Deuda Técnica
- API.md desactualizado (faltan 10 endpoints nuevos)
- Sin tests automatizados
- employee_number debería ser por juego, no global

---

## 📈 Métricas

**Líneas de Código Nuevas**: ~1400  
**Archivos Nuevos**: 1 (time_manager.py)  
**Archivos Significativamente Modificados**: 5  
**Endpoints Nuevos**: 10  
**Tablas Nuevas**: 1 (employee_tasks)  
**Funcionalidades Completas Nuevas**: 3 (Contratación, Temporal, Notificaciones)

---

## 💡 Comandos Útiles

```bash
# Iniciar servidor
uvicorn app.main:app --reload

# Ver cola de tareas
sqlite3 data/spacegom.db "SELECT * FROM employee_tasks WHERE game_id='test' ORDER BY queue_position;"

# Ver eventos pendientes
sqlite3 data/spacegom.db "SELECT state FROM games WHERE id='test';" | jq '.event_queue'

# Limpiar partida de prueba
rm -rf data/games/test
```

---

**Última actualización**: 2026-01-09 13:54  
**Versión**: 3.0  
**Estado**: Funcional y probado ✅  
**Próximo objetivo**: Navegación entre Áreas + Pantalla de Selección
