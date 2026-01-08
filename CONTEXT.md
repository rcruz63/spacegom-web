# Spacegom Companion - Contexto de Proyecto

Este documento resume el estado actual del desarrollo para permitir la continuación del proyecto en sesiones futuras.

## Estado del Proyecto
Aplicación web tipo "Companion" para el juego Spacegom, desarrollada con FastAPI, Jinja2 y JavaScript/CSS moderno.

### Estado Actual (Sesión Actualizada: 2026-01-08)

1.  **Setup Inicial Completado y Refinado**:
    *   ✅ **Nave Inicial Bloqueada**: El modelo de nave está fijo a `Basic Starfall` para nuevas aventuras (herencia).
    *   ✅ **Búsqueda Consecutiva de Planetas**: Implementada la lógica de búsqueda secuencial (111 → 112 → 113...) según reglas del manual.
    *   ✅ **Validación de Planetas**: Verificación automática de requisitos (Tecnología, Población, Convenio, Soporte Vital, Productos).
    *   ✅ **NUEVO: Selección de Dificultad**: Fácil (600 SC), Normal (500 SC), Difícil (400 SC)
    *   ✅ **NUEVO: Personal Inicial**: 11 empleados creados automáticamente (76 SC/mes total)

2.  **Backend & Datos**:
    *   Importación de 216 planetas desde Excel a SQLite.
    *   **NUEVO: Tabla `personnel`** para gestión de empleados por partida.
    *   Sistema de persistencia de partidas (`GameState`) en archivos JSON con campos nuevos: `difficulty`, `treasury`, `reputation`, `transactions`.
    *   Definición de modelos de naves y sus estadísticas en `app/ship_data.py`.
    *   **NUEVO: 7 endpoints API** para gestión de personal y tesorería.

3.  **Dashboard**:
    *   HUD funcional: Combustible, Almacén, Calendario, Reputación
    *   **NUEVO: Tesorería** (saldo en SC) y **Gastos/Mes** (salarios)
    *   **NUEVO: Navegación rápida** con botones a Personal (👥) y Tesorería (💰)
    *   Cuadrícula de navegación (6x6) con fondo de estrellas generado por CSS.
    *   Historial de Mundos (Archivos Estelares) que permite ver detalles de planetas descubiertos.
    *   Mapeo único de planetas: Cada mundo se "ancla" a un cuadrante específico por partida.

4.  **NUEVO: Sistema de Personal** (/personnel):
    *   Lista de empleados activos
    *   Contratar/Despedir personal
    *   Ver experiencia (N/E/V) y moral (B/M/A)
    *   Cálculo automático de salarios totales

5.  **NUEVO: Sistema de Tesorería** (/treasury):
    *   Visualización de saldo actual
    *   Registro de transacciones (ingresos/gastos)
    *   Categorías: Comercio, Misión, Suministros, Reparaciones, etc.
    *   Historial completo de movimientos

6.  **Lógica de Juego**:
    *   Implementación de localizaciones en el planeta (Mundo, Puerto, Orbital, Estación).
    *   Lógica de navegación entre Áreas (Columnas A ↔ F) respetando límites.

## Mecánicas del Juego (Basadas en @files/)

### Calendario Spacegom
- **Meses**: 12 meses al año
- **Días por Mes**: **35 días** (no 30 como en el calendario estándar)
- **Días Administrativos**:
  - Día 28: Administración semanal
  - Día 35: Administración mensual

### Sistema de Reputación
- **Rango**: De **-5** a **+5**
- **Impacto**: Afecta precios de mercado, acceso a misiones y eventos aleatorios

### Sistema de Daños
- **Progresión**: Leve → Moderado → Grave
- **Niveles**:
  - **Leve**: 3 casillas (Basic Starfall)
  - **Moderado**: 2 casillas
  - **Grave**: 2 casillas
- **Crítico**: Al completar daños graves → **HIPERSALTO DESTRUIDO**

### Gestión de Almacenes
Existen **dos tipos de almacenamiento** distintos en el juego:

#### Capacidad de Carga de la Nave
- **Basic Starfall**: 40 UCN (Unidades de Carga Normalizada)
- Representa la bodega física de la nave
- Varía según el modelo de nave (ver `ship_data.py`)
- Límite físico que no se puede exceder durante el vuelo

#### Almacén de la Compañía
- Depósito de mercancías en el planeta base
- **Capacidad**: Por determinar según reglas del manual
- Permite almacenar mercancías sin ocupar espacio en la nave
- Útil para especulación y comercio a largo plazo

### Búsqueda de Planeta Inicial (Regla 📕)
Si el código 3d6 inicial no es apto para el inicio, se debe consultar el **siguiente código válido** en orden secuencial:
- Ejemplo: 111 → 112 → 113 → 114 → 115 → 116 → 121 → 122...
- Hasta encontrar un planeta que cumpla **todos** los requisitos de inicio.

### Requisitos para Planeta de Inicio
1. **Población** > 1000 habitantes
2. **Nivel Tecnológico**: No puede ser PR (Primitivo) ni RUD (Rudimentario)
3. **Soporte Vital**: No puede ser TA (Traje con Asistencia) ni TH (Traje Hostil)
4. **Convenio Spacegom**: Debe tener Sí
5. **Productos**: Debe tener al menos un producto disponible

## Estructura de Archivos Clave

### Backend
*   `app/main.py`: Endpoints de la API y rutas web.
*   `app/game_state.py`: Lógica de persistencia y métodos de descubrimiento/navegación.
*   `app/ship_data.py`: Tabla de naves y sugeridores de nombres.
*   `app/dice.py`: Utilidades de dados, incluye `get_next_planet_code()`.
*   `app/database.py`: Modelos SQLAlchemy para planetas.

### Frontend
*   `app/templates/dashboard.html`: Interfaz principal y lógica JS del HUD/Grid.
*   `app/templates/setup.html`: Proceso de creación de partida (ahora refinado).
*   `app/templates/index.html`: Página de inicio con navegación.

### Datos
*   `data/Base_de_datos_de_planetas.xlsx`: Fuente de datos original.
*   `data/spacegom.db`: Base de datos SQLite con 216 planetas.
*   `data/games/{game_id}/state.json`: Estado persistente de cada partida.

### Documentación de Referencia
*   `files/`: Materiales originales del juego de mesa y archivos de datos:
    - PDFs: Calendario de Campaña, Ficha de Compañía, Hoja de Mundos, Tesorería
    - CSV: nombres_megacorp.csv (470), nombres_naves.csv (500), nombres_personal.csv (1000)
    - Pack completo con todos los descargables

## Decisiones de Diseño

*   **Estética**: "Retro-Futurista / Neon-Blue" con micro-animaciones en el grid.
*   **Navegación**: Los planetas se identifican por sus códigos de 3 dígitos (111-666).
*   **Persistencia**: Se usa una carpeta `data/games/{game_id}/` para separar los datos de cada partida.
*   **Herencia**: Para el inicio de aventura, la nave es siempre Basic Starfall (no modificable).

## Próximos Pasos

### Implementación Pendiente
- [ ] **Sistema de Eventos Aleatorios**: Motor de eventos diarios/de viaje
- [ ] **Calendario Dinámico**: Ajustar lógica de avance de tiempo a meses de 35 días
- [ ] **Sistema de Combate**: Diseñar interfaz de combate y resolución
- [ ] **Mejora de Nave**: Sistema de astilleros para cambiar modelo o reparar daños
- [ ] **Gestión de Carga**: Implementar límites de peso/volumen basados en modelo de nave
- [ ] **Misiones y Contratos**: Sistema de misiones procedurales

### Mejoras de UX
- [ ] Animaciones de transición entre secciones del setup
- [ ] Tooltips informativos en el dashboard
- [ ] Modo tutorial/ayuda contextual

---

*Contexto actualizado el 2026-01-08 después de refinamientos de setup inicial y documentación.*
