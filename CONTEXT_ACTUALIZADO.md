# SPACEGOM-WEB - Contexto Actualizado (2026-01-20)

## 📝 Resumen Ejecutivo

Aplicación web para gestionar partidas del juego de mesa **Spacegom**, desarrollada con FastAPI. Estado actual: **Sistema Completo + Documentación Técnica Exhaustiva (29 archivos) - Totalmente Funcional y Preparado para Continuación por Otros Desarrolladores**.

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
   - Navegación global a subsistemas
   - **LIMPIO**: Eliminados componentes obsoletos

3. **Sistema de Personal** (/personnel)
   - **Contratación Automatizada**: Modal con 29 puestos, filtrado por tech level, cálculo de salario y tiempos.
   - **Cola de Tareas del Director**: Gestión ordenada de contrataciones.
   - **Avance Temporal**: Resolución automática de eventos con tiradas y modificadores.

4. **Sistema de Comercio de Mercancías** (/trade) ⭐ NUEVO
   - **Terminal de Comercio**:
     - Vista de OFERTA (Comprar) filtrada por capacidad productiva del planeta.
     - Vista de DEMANDA (Vender) filtrada por stock y restricciones de producción local.
     - Ledger (Registro de Pedidos) con histórico de transacciones (trazabilidad).
   - **Lógica de Negocio**:
     - Negociación de precios con tiradas 2d6 (Manual/Auto).
     - Modificadores por Reputación y Habilidad.
     - Restricción de venta (no vender producto donde se produce).
     - Tracking de Fechas (DD-MM-YYYY) y beneficio.
   - **Base de Datos**: Tabla `trade_orders` dedicada.

5. **Sistema de Transporte de Pasajeros** ⭐ NUEVO
   - **Widget en Dashboard**: Visible solo en superficie planetaria.
   - **Lógica de Negocio**: Cálculo de capacidad vs demanda, ingresos x auxiliares.
   - **Reglas Universales**: Moral/Experiencia integrada.

6. **Sistema de Notificaciones & UX**
   - **Toast Notifications**: Feedback no bloqueante (Success/Error/Info).
   - **Panel Lateral**: Detalles de resultados de tiradas y eventos.

7. **Sistema Temporal** (`time_manager.py`)
   - **GameCalendar**: Gestión de fechas personalizada (35 días/mes).
   - **EventQueue**: Cola de eventos futuros.

8. **Sistemas Base** (/treasury, /missions)
   - Gestión de tesorería y misiones de campaña operativa.

9. **Documentación Técnica Completa** 📚 ⭐ NUEVO
   - **29 archivos de documentación** generados automáticamente en `docs/`
   - **Cobertura completa**: Todos los módulos Python, JS y HTML templates
   - **Detalles técnicos**: Funciones, clases, dependencias, ejemplos de uso
   - **README actualizado**: Estructura completa del proyecto y guías de instalación

---

## 🗄️ Estructura de Base de Datos

### Tablas Principales
- `games`: Estado serializado (JSON).
- `planets`: Datos estáticos de 216 planetas.
- `personnel`: Lista de empleados.
- `missions`: Objetivos y estado.

### Tabla `trade_orders` (NUEVA)
```python
- id, game_id, area
- buy_planet_code, product_code, quantity
- buy_price_per_unit, total_buy_price, buy_date
- sell_planet_code, total_sell_price, sell_date, profit
- status (in_transit/sold), traceability (bool)
```

### Tabla `employee_tasks`
```python
- id, game_id, employee_id
- task_type ("hire_search")
- status, queue_position, task_data (JSON), result_data (JSON)
- Timestamps: created, started, completion, finished
```

---

## 🔌 API Endpoints Clave

### Comercio (NUEVO)
- `GET /api/games/{id}/trade/market` - Datos de mercado (compra/venta)
- `GET /api/games/{id}/trade/orders` - Historial de pedidos
- `POST /api/games/{id}/trade/negotiate` - Simulación de negociación (dados manuales/auto)
- `POST /api/games/{id}/trade/buy` - Ejecutar compra
- `POST /api/games/{id}/trade/sell` - Ejecutar venta

### Personal y Tiempo
- `POST /api/games/{id}/hire/start` - Iniciar contratación
- `POST /api/games/{id}/time/advance` - Avanzar tiempo y resolver cola

---

## 📂 Estructura del Proyecto

```
spacegom-web/
├── app/
│   ├── main.py                # Endpoints registrados
│   ├── database.py            # Modelos (incluye TradeOrder)
│   ├── game_state.py
│   ├── trade_manager.py       # NUEVO - Lógica de negocio comercio
│   ├── time_manager.py
│   └── templates/
│       ├── base.html          # Nav global actualizada
│       ├── dashboard.html
│       ├── personnel.html
│       ├── trade.html         # NUEVO - Terminal de comercio
│       └── ...
├── docs/                      # NUEVO - Documentación técnica completa
│   ├── main.md                # API FastAPI completa
│   ├── database.md            # Configuración BD y modelos
│   ├── trade_manager.md       # Lógica de comercio
│   ├── personnel_manager.md   # Gestión de personal
│   ├── dice.md                # Sistema de dados
│   └── ...                    # 23 archivos adicionales
├── data/
│   └── spacegom.db
```

---

## 🚀 Próximos Pasos

### Alta Prioridad
1. **Navegación Entre Áreas**
   - Selector de área explorada y persistencia.
   - Switch entre cuadrantes.

2. **Pantalla de Selección de Partidas**
   - Landing page para cargar/crear partidas.

### Media Prioridad
3. **Mejoras UX**
   - Fix fondo estrellado.
   - Reordenar cola de tareas (Drag & Drop).

### Implementaciones Futuras
4. **Eventos Aleatorios**
5. **Mejoras de Nave**

---

## 📈 Métricas Actualizadas

**Líneas de Código Nuevas**: ~2000+
**Archivos Nuevos**: `trade_manager.py`, `trade.html`
**Endpoints Nuevos**: ~20 total
**Tablas Nuevas**: 3 (`employee_tasks`, `missions`, `trade_orders`)
**Funcionalidades Completas**: 5 (Personal, Tiempo, Notificaciones, Misiones, Comercio)
**Archivos de Documentación**: 29 archivos técnicos completos en `docs/`
**Cobertura de Documentación**: 100% (todos los módulos Python, JS y HTML)

---

**Última actualización**: 2026-01-20
**Versión**: 3.3
**Estado**: Completamente funcional y documentado para continuación por otros desarrolladores ✅
