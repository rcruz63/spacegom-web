# database.py - Modelos de Base de Datos

## Overview

Este módulo define todos los modelos SQLAlchemy para la base de datos SQLite del proyecto. Incluye modelos para planetas, personal, misiones, comercio y tareas de empleados.

**Ubicación**: `app/database.py`
**Líneas**: 591
**Dependencias**: `sqlalchemy`, `os`

## Configuración de Base de Datos

```python
DATABASE_DIR = "data"
DATABASE_PATH = f"{DATABASE_DIR}/spacegom.db"
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## Modelo Planet

### Campos Principales

#### Identificación
- `code`: Código 3d6 (111-666), clave primaria
- `name`: Nombre del planeta

#### Soporte Vital
- `life_support`: Tipo requerido (NO, SO, MF, RE, RF, TE, TA, TH)
- `local_contagion_risk`: Riesgo de contagio (SI/NO)
- `days_to_hyperspace`: Días hasta estación de hiperdisparo
- `legal_order_threshold`: Umbral de ordenamiento legal

#### Espaciopuerto
- `spaceport_quality`: Calidad (EXC, NOT, MED, BAS, RUD, SIN)
- `fuel_density`: Densidad de combustible (DB, DM, DA, N)
- `docking_price`: Precio de amarre

#### Instalaciones Orbitales
- `orbital_cartography_center`: Centro de cartografía
- `orbital_hackers`: Piratas informáticos
- `orbital_supply_depot`: Depósito de suministros
- `orbital_astro_academy`: Academia de astronavegación

#### Productos Disponibles
Campos booleanos para productos: INDU, BASI, ALIM, MADE, AGUA, MICO, MIRA, MIPR, PAVA, A, AE, AEI, COM

#### Información Comercial
- `self_sufficiency_level`: Nivel de autosuficiencia
- `ucn_per_order`: UCN por pedido
- `max_passengers`: Máximo de pasajeros
- `mission_threshold`: Umbral de misiones

#### Validación para Inicio
- `tech_level`: Nivel tecnológico (PR, RUD, ES, INT, POL, N.S)
- `population_over_1000`: Población > 1000
- `convenio_spacegom`: Adscrito al convenio

#### Notas
- `notes`: Notas editables
- `is_custom`: Planeta personalizado

## Modelo Personnel

### Campos
- `id`: ID autoincremental
- `game_id`: FK al juego
- `position`: Puesto de trabajo
- `name`: Nombre completo
- `monthly_salary`: Salario en SC
- `experience`: N/E/V (Novato/Experto/Veterano)
- `morale`: B/M/A (Baja/Media/Alta)
- `hire_date`: Fecha de contratación
- `is_active`: Estado activo/inactivo
- `notes`: Notas adicionales

### Personal Inicial
Lista de 11 empleados creados automáticamente al completar setup.

## Modelo Mission

### Campos
- `id`: ID autoincremental
- `game_id`: FK al juego
- `mission_type`: "campaign" o "special"
- `origin_world`: Planeta de origen
- `execution_place`: Lugar de ejecución
- `max_date`: Fecha máxima
- `result`: "", "exito", "fracaso"
- `objective_number`: Para objetivos de campaña
- `mission_code`: Código de misión especial
- `book_page`: Página del libro
- `created_date`: Fecha de creación
- `completed_date`: Fecha de completación
- `notes`: Notas

## Modelo TradeOrder

### Campos
- `id`: ID autoincremental
- `game_id`: FK al juego
- `area`: Área del pedido
- `buy_planet_code`: Planeta de compra
- `product_code`: Código del producto
- `quantity`: Cantidad
- `buy_price_per_unit`: Precio unitario de compra
- `total_buy_price`: Precio total de compra
- `buy_date`: Fecha de compra
- `traceability`: Cumple convenio Spacegom
- `status`: "in_transit", "sold"
- `sell_planet_code`: Planeta de venta
- `sell_price_total`: Precio total de venta
- `sell_date`: Fecha de venta
- `profit`: Ganancia/pérdida

## Modelo EmployeeTask

### Campos
- `id`: ID autoincremental
- `game_id`: FK al juego
- `employee_id`: FK a personal
- `task_type`: Tipo de tarea ("hire_search", etc.)
- `status`: "pending", "in_progress", "completed", "failed"
- `queue_position`: Posición en cola
- `task_data`: JSON con datos específicos
- `created_date`: Fecha de creación
- `started_date`: Fecha de inicio
- `completion_date`: Fecha de completación esperada
- `finished_date`: Fecha real de finalización
- `result_data`: JSON con resultado

## Constantes y Catálogos

### Diccionarios de Referencia
- `LIFE_SUPPORT_TYPES`: Descripciones de tipos de soporte vital
- `SPACEPORT_QUALITY`: Descripciones de calidad de espaciopuerto
- `FUEL_DENSITY`: Descripciones de densidad de combustible
- `PRODUCT_DESCRIPTIONS`: Descripciones de productos

### Catálogo de Puestos
`POSITIONS_CATALOG`: Diccionario con configuración de cada puesto:
- `tech_level`: Nivel tecnológico requerido
- `search_time_dice`: Dados para tiempo de búsqueda
- `base_salary`: Salario base
- `hire_threshold`: Umbral de contratación

### Requisitos Tecnológicos
`TECH_LEVEL_REQUIREMENTS`: Mapeo de niveles tecnológicos a códigos válidos.

## Funciones de Utilidad

### `init_db()`
Crea todas las tablas en la base de datos.

### `get_db()`
Generador de sesiones de base de datos para inyección de dependencias.

## Dependencias

- **SQLAlchemy**: ORM completo
- **os**: Creación de directorios

## Notas de Implementación

- **SQLite**: Base de datos simple, sin servidor
- **Foreign Keys**: Implícitas mediante `game_id`
- **JSON Fields**: `task_data` y `result_data` almacenan JSON como texto
- **Enums**: Usados campos string para flexibilidad
- **Initial Data**: Personal inicial creado en setup
- **Validation**: Lógica de negocio en endpoints, no en modelos

## Mejores Prácticas

- Usar `get_db()` como dependencia FastAPI
- Mantener consistencia en formatos de fecha
- Validar datos en endpoints antes de commit
- Usar transacciones para operaciones complejas
- Documentar campos con comentarios detallados