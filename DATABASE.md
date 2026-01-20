# Documentación de la Base de Datos

## 📚 Documentación Técnica Relacionada

Para información detallada sobre la implementación de la base de datos y modelos SQLAlchemy, consulta:

- **[docs/database.md](docs/database.md)**: Configuración completa de base de datos y modelos
- **[docs/models.md](docs/models.md)**: Modelos de datos adicionales y esquemas
- **[docs/main.md](docs/main.md)**: Endpoints de API relacionados con la base de datos

## Tabla: `planets`

La tabla `planets` contiene toda la información de los 216 planetas del universo Spacegom, basados en el sistema de coordenadas 3d6 (códigos 111-666).

### Esquema de la Tabla

#### Identificación
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | INTEGER | Clave primaria. Código 3d6 del planeta (111-666) |
| `name` | VARCHAR | Nombre del planeta |
| `is_custom` | BOOLEAN | Indica si es un planeta personalizado creado durante la partida |

#### Soporte Vital
| Campo | Tipo | Valores Posibles | Descripción |
|-------|------|-----------------|-------------|
| `life_support` | VARCHAR | NO, SO, MF, RE, RF, TE, TA, TH | Tipo de soporte vital necesario |
| `local_contagion_risk` | VARCHAR | SI, NO | Riesgo de contagio local |
| `days_to_hyperspace` | FLOAT | - | Días de viaje hasta la estación de hiperdisparo más cercana |
| `legal_order_threshold` | VARCHAR | "N+" | Umbral de ordenamiento legal (valor a igualar o superar en 2d6) |

**Códigos de Soporte Vital**:
- **NO**: No es necesario ningún soporte vital
- **SO**: Suministro básico de oxígeno
- **MF**: Máscara con filtraje
- **RE**: Respirador
- **RF**: Respirador con filtraje
- **TE**: Traje espacial estándar
- **TA**: Traje espacial avanzado
- **TH**: Traje espacial hiperavanzado

#### Espaciopuerto
| Campo | Tipo | Valores Posibles | Descripción |
|-------|------|-----------------|-------------|
| `spaceport_quality` | VARCHAR | EXC, NOT, MED, BAS, RUD, SIN | Calidad del espaciopuerto |
| `fuel_density` | VARCHAR | DB, DM, DA, N | Tipo de combustible disponible |
| `docking_price` | INTEGER | 0-9 | Precio de amarre |

**Calidad del Espaciopuerto**:
- **EXC**: Excelente
- **NOT**: Notable
- **MED**: Medio
- **BAS**: Básico
- **RUD**: Rudimentario
- **SIN**: Sin espaciopuerto

**Tipo de Combustible**:
- **DB**: Densidad Baja
- **DM**: Densidad Media
- **DA**: Densidad Alta
- **N**: Ninguno

#### Instalaciones Orbitales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `orbital_cartography_center` | BOOLEAN | Centro de Cartografía (CC) |
| `orbital_hackers` | BOOLEAN | Piratas Informáticos (PI) |
| `orbital_supply_depot` | BOOLEAN | Depósito de Suministros (DS) |
| `orbital_astro_academy` | BOOLEAN | Academia de Astronavegación (AA) |

#### Productos Disponibles
| Campo | Tipo | Código | Descripción |
|-------|------|--------|-------------|
| `product_indu` | BOOLEAN | INDU | Productos industriales y manufacturados comunes |
| `product_basi` | BOOLEAN | BASI | Metal, plásticos, productos químicos y otros materiales básicos elaborados |
| `product_alim` | BOOLEAN | ALIM | Productos de alimentación |
| `product_made` | BOOLEAN | MADE | Madera y derivados |
| `product_agua` | BOOLEAN | AGUA | Agua potable |
| `product_mico` | BOOLEAN | MICO | Minerales comunes |
| `product_mira` | BOOLEAN | MIRA | Minerales raros y materias primas poco comunes |
| `product_mipr` | BOOLEAN | MIPR | Metales preciosos, diamantes, gemas |
| `product_pava` | BOOLEAN | PAVA | Productos avanzados, computadores modernos, robótica y otros equipos |
| `product_a` | BOOLEAN | A | Armas hasta etapa espacial |
| `product_ae` | BOOLEAN | AE | Armas a partir de etapa espacial |
| `product_aei` | BOOLEAN | AEI | Armas modernas a partir de etapa interestelar |
| `product_com` | BOOLEAN | COM | Combustible para astronavegación |

#### Información Comercial
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `self_sufficiency_level` | FLOAT | Nivel de autosuficiencia. Positivo: produce más de lo que necesita. Negativo: necesita más de lo que produce |
| `ucn_per_order` | FLOAT | Unidades de Crédito Normalizadas (UCN) por pedido |
| `max_passengers` | FLOAT | Número máximo de pasajeros que acepta el planeta |
| `mission_threshold` | VARCHAR | Umbral para obtener misiones (valor a igualar o superar en 2d6, ej: "7+") |

#### Validación para Planeta Inicial
| Campo | Tipo | Valores Posibles | Descripción |
|-------|------|-----------------|-------------|
| `tech_level` | VARCHAR | PR, RUD, ES, INT, POL, N.S | Nivel tecnológico del planeta |
| `population_over_1000` | BOOLEAN | - | Indica si la población es mayor a 1000 habitantes |
| `convenio_spacegom` | BOOLEAN | - | Indica si está adscrito al Convenio Universal Spacegom |

**Niveles Tecnológicos**:
- **PR**: Primitivo
- **RUD**: Rudimentario
- **ES**: Estándar
- **INT**: Intermedio
- **POL**: Pólvora
- **N.S**: No Significativo

**Requisitos para Planeta Inicial**:
Un planeta es válido como punto de partida si cumple:
1. `population_over_1000 = true`
2. `tech_level` no es PR ni RUD
3. `life_support` no es TA ni TH
4. `convenio_spacegom = true`
5. Al menos un producto disponible

#### Notas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `notes` | TEXT | Campo editable desde el frontend para notas personalizadas del jugador |

---

## Ejemplo de Registro

**Planeta 111: Chipethea**

```sql
SELECT * FROM planets WHERE code = 111;
```

```
code: 111
name: Chipethea
life_support: NO
local_contagion_risk: NO
days_to_hyperspace: 7.0
legal_order_threshold: 5+
spaceport_quality: MED
fuel_density: DB
docking_price: 2
orbital_cartography_center: 0 (false)
orbital_hackers: 1 (true)
orbital_supply_depot: 0 (false)
orbital_astro_academy: 0 (false)
product_indu: 1 (true)
product_basi: 1 (true)
product_alim: 1 (true)
product_made: 1 (true)
product_agua: 1 (true)
product_mico: 1 (true)
product_mira: 0 (false)
product_mipr: 0 (false)
product_pava: 0 (false)
product_a: 1 (true)
product_ae: 0 (false)
product_aei: 0 (false)
product_com: 0 (false)
self_sufficiency_level: 1.0
ucn_per_order: 10.0
max_passengers: 7.0
mission_threshold: 10+
tech_level: NULL (se rellena durante setup)
population_over_1000: 1 (true)
convenio_spacegom: 1 (true)
notes: ""
is_custom: 0 (false)
```

---

## Consultas Útiles

### Encontrar planetas válidos para inicio
```sql
SELECT code, name, tech_level, life_support
FROM planets
WHERE population_over_1000 = 1
  AND convenio_spacegom = 1
  AND life_support NOT IN ('TA', 'TH')
  AND tech_level NOT IN ('PR', 'RUD')
  AND tech_level IS NOT NULL
  AND (product_indu = 1 OR product_basi = 1 OR product_alim = 1 
       OR product_made = 1 OR product_agua = 1 OR product_mico = 1
       OR product_mira = 1 OR product_mipr = 1 OR product_pava = 1
       OR product_a = 1 OR product_ae = 1 OR product_aei = 1
       OR product_com = 1);
```

### Planetas con Centro de Cartografía
```sql
SELECT code, name, spaceport_quality
FROM planets
WHERE orbital_cartography_center = 1;
```

### Planetas que venden combustible
```sql
SELECT code, name, fuel_density, docking_price
FROM planets
WHERE fuel_density IN ('DB', 'DM', 'DA')
ORDER BY docking_price;
```

### Planetas con alta autosuficiencia
```sql
SELECT code, name, self_sufficiency_level, ucn_per_order
FROM planets
WHERE self_sufficiency_level > 5
ORDER BY self_sufficiency_level DESC;
```

---

## Fuente de Datos

Los planetas son importados desde:
- **Archivo**: `data/Base_de_datos_de_planetas_simple.xlsx`
- **Script**: `app/import_planets.py`
- **Total**: 216 planetas (códigos 3d6 válidos)

El script de importación:
1. Lee el Excel con cabeceras simplificadas
2. Parsea el campo "Espaciopuerto" (formato XXX-ZZ-N) en 3 campos separados
3. Convierte las instalaciones orbitales de columnas separadas a campos booleanos
4. Valida tipos de datos y aplica valores por defecto

---

## Mantenimiento

### Reimportar planetas
```bash
# Eliminar base de datos actual
rm data/spacegom.db

# Ejecutar script de importación
python -m app.import_planets
```

### Añadir notas a un planeta
```bash
curl -X POST http://localhost:8000/api/planets/111/update-notes \
  -F "notes=Este planeta tiene excelentes oportunidades comerciales"
```

### Ver estructura de la tabla
```bash
sqlite3 data/spacegom.db ".schema planets"
```


---

## Tabla: `personnel`

La tabla `personnel` contiene todos los empleados de cada partida. Cada juego tiene su propia plantilla de personal que se crea automáticamente al completar el setup.

### Esquema de la Tabla

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | Clave primaria (autoincremental) |
| `game_id` | VARCHAR | ID del juego al que pertenece el empleado |
| `position` | VARCHAR | Puesto de trabajo del empleado |
| `name` | VARCHAR | Nombre completo del empleado |
| `monthly_salary` | INTEGER | Salario mensual en SC (Créditos Spacegom) |
| `experience` | VARCHAR | Nivel de experiencia: N (Novato), E (Experto), V (Veterano) |
| `morale` | VARCHAR | Nivel de moral: B (Baja), M (Media), A (Alta) |
| `hire_date` | VARCHAR | Fecha de contratación (formato ISO: YYYY-MM-DD) |
| `is_active` | BOOLEAN | True si está activo, False si fue despedido |
| `notes` | TEXT | Notas adicionales sobre el empleado |

### Personal Inicial

Al completar el setup, se crean automáticamente 11 empleados:

| ID | Puesto | Nombre | Salario | Exp | Moral |
|----|--------|--------|---------|-----|-------|
| 1 | Director gerente | Widaker Farq | 20 SC | V | A |
| 2 | Comandante de hipersaltos | Samantha Warm | 15 SC | V | M |
| 3 | Ingeniero computacional | Thomas Muller | 4 SC | N | B |
| 4 | Ingeniero de astronavegación | Walter Lopez | 8 SC | N | B |
| 5 | Técnico de repostaje y análisis | Jeffrey Cook | 8 SC | E | B |
| 6 | Piloto | Danielle Rivers | 10 SC | E | B |
| 7 | Operario de logística y almacén | Isaac Peterson | 1 SC | N | B |
| 8 | Contabilidad y burocracia | Katherine Smith | 3 SC | E | M |
| 9 | Suministros de mantenimiento | Jason Wilson | 3 SC | E | B |
| 10 | Cocinero | Sam Hernández | 3 SC | E | M |
| 11 | Asistente doméstico | Alexandra Adams | 1 SC | E | B |

**Total salarios mensuales iniciales**: 76 SC

### Ejemplo de Registro

```sql
SELECT * FROM personnel WHERE game_id = 'test_game' AND id = 1;
```

```
id: 1
game_id: test_game
position: Director gerente
name: Widaker Farq
monthly_salary: 20
experience: V
morale: A
hire_date: 2026-01-08
is_active: 1 (true)
notes: ""
```

### Consultas Útiles

**Listar personal activo de un juego**:
```sql
SELECT name, position, monthly_salary, experience, morale
FROM personnel
WHERE game_id = 'test_game' AND is_active = 1
ORDER BY monthly_salary DESC;
```

**Calcular salarios totales**:
```sql
SELECT SUM(monthly_salary) as total_salaries
FROM personnel
WHERE game_id = 'test_game' AND is_active = 1;
```

**Personal por nivel de experiencia**:
```sql
SELECT experience, COUNT(*) as count, SUM(monthly_salary) as total_cost
FROM personnel
WHERE game_id = 'test_game' AND is_active = 1
GROUP BY experience;
```

**Empleados con baja moral**:
```sql
SELECT name, position, morale
FROM personnel
WHERE game_id = 'test_game' AND is_active = 1 AND morale = 'B';
```

---

---

## Tabla: `missions`

La tabla `missions` gestiona tanto los objetivos de campaña como las misiones especiales del juego.

### Esquema de la Tabla

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | Clave primaria |
| `game_id` | VARCHAR | ID del juego |
| `mission_type` | VARCHAR | Tipo: "campaign" o "special" |
| `origin_world` | VARCHAR | Código/nombre del planeta de origen |
| `execution_place` | VARCHAR | Lugar donde se ejecuta la misión |
| `max_date` | VARCHAR | Fecha límite (formato juego o DD-MM-YY) |
| `result` | VARCHAR | Estado: "" (activa), "exito", "fracaso" |
| `objective_number` | INTEGER | Solo campañas: Número de objetivo (ej: 1) |
| `mission_code` | VARCHAR | Solo especiales: Código (ej: "M-47") |
| `book_page` | INTEGER | Solo especiales: Página del libro |
| `created_date` | VARCHAR | Fecha de aceptación |
| `completed_date` | VARCHAR | Fecha de finalización |
| `notes` | TEXT | Notas adicionales |

---

## Tabla: `trade_orders`

La tabla `trade_orders` gestiona el sistema de comercio de mercancías entre planetas. Cada fila representa un pedido de compra/venta en la terminal comercial.

### Esquema de la Tabla

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | Clave primaria (autoincremental) |
| `game_id` | VARCHAR | ID del juego al que pertenece el pedido |
| `area` | INTEGER | Área espacial donde se realiza el comercio (1-12) |

#### Información de Compra
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `buy_planet_code` | INTEGER | Código del planeta donde se compra (111-666) |
| `buy_planet_name` | VARCHAR | Nombre del planeta de compra (cache) |
| `product_code` | VARCHAR | Código del producto (INDU, BASI, ALIM, etc.) |
| `quantity` | INTEGER | Cantidad en Unidades de Crédito Normalizado (UCN) |
| `buy_price_per_unit` | INTEGER | Precio de compra por unidad (SC) |
| `total_buy_price` | INTEGER | Precio total de compra (SC) |
| `buy_date` | VARCHAR | Fecha de compra (formato YYYY-MM-DD) |

#### Información de Venta
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `sell_planet_code` | INTEGER | Código del planeta donde se vende (opcional) |
| `sell_planet_name` | VARCHAR | Nombre del planeta de venta (opcional, cache) |
| `sell_price_total` | INTEGER | Precio total de venta (SC, opcional) |
| `sell_date` | VARCHAR | Fecha de venta (formato YYYY-MM-DD, opcional) |
| `profit` | INTEGER | Ganancia/pérdida calculada (SC, opcional) |

#### Estado y Control
| Campo | Tipo | Valores Posibles | Descripción |
|-------|------|------------------|-------------|
| `status` | VARCHAR | "in_transit", "sold" | Estado del pedido |
| `traceability` | BOOLEAN | true, false | Cumple Convenio Spacegom (afecta ventas) |

#### Metadata
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `created_at` | VARCHAR | Timestamp de creación del registro |
| `updated_at` | VARCHAR | Timestamp de última actualización |

### Reglas de Negocio

#### Límite por Área
- **Máximo 25 pedidos** por área espacial
- Controlado por lógica de aplicación (no constraint de BD)

#### Trazabilidad del Convenio
- **True**: Pedido cumple Convenio Spacegom
- **False**: Perdida de trazabilidad (venta en planetas no adscritos)
- Afecta restricciones de venta en mercados locales

#### Estados del Pedido
- **"in_transit"**: Comprado y almacenado (o en proceso de carga)
- **"sold"**: Vendido y completado

### Ejemplo de Registro

**Pedido de compra de productos industriales:**

```sql
SELECT * FROM trade_orders WHERE id = 1;
```

```
id: 1
game_id: game_123
area: 7
buy_planet_code: 245
buy_planet_name: "Aldoria Prime"
product_code: "INDU"
quantity: 50
buy_price_per_unit: 8
total_buy_price: 400
buy_date: "2026-01-15"
sell_planet_code: NULL
sell_planet_name: NULL
sell_price_total: NULL
sell_date: NULL
profit: NULL
status: "in_transit"
traceability: true
created_at: "2026-01-15T10:30:00Z"
updated_at: "2026-01-15T10:30:00Z"
```

### Consultas Útiles

#### Pedidos activos por área
```sql
SELECT product_code, quantity, total_buy_price, buy_date
FROM trade_orders
WHERE game_id = 'game_123'
  AND area = 7
  AND status = 'in_transit'
ORDER BY buy_date DESC;
```

#### Historial de ganancias/pérdidas
```sql
SELECT 
    product_code,
    quantity,
    total_buy_price,
    sell_price_total,
    profit,
    (profit * 100.0 / total_buy_price) as profit_percentage
FROM trade_orders
WHERE game_id = 'game_123'
  AND status = 'sold'
  AND profit IS NOT NULL
ORDER BY profit DESC;
```

#### Pedidos sin trazabilidad
```sql
SELECT buy_planet_name, product_code, quantity
FROM trade_orders
WHERE game_id = 'game_123'
  AND traceability = false
  AND status = 'in_transit';
```

#### Resumen por área
```sql
SELECT 
    area,
    COUNT(*) as total_orders,
    SUM(CASE WHEN status = 'in_transit' THEN 1 ELSE 0 END) as in_transit,
    SUM(CASE WHEN status = 'sold' THEN profit ELSE 0 END) as total_profit
FROM trade_orders
WHERE game_id = 'game_123'
GROUP BY area
ORDER BY area;
```

### Integración con Frontend

#### API Endpoints Relacionados
- `GET /api/games/{game_id}/trade/orders` - Lista pedidos por área
- `POST /api/games/{game_id}/trade/buy` - Crear pedido de compra
- `POST /api/games/{game_id}/trade/sell` - Ejecutar venta

#### Flujo Típico
1. **Compra**: Usuario selecciona producto → Se crea registro con `status = "in_transit"`
2. **Viaje**: Nave transporta mercancía entre planetas
3. **Venta**: Usuario vende → Se actualizan campos de venta y `profit`

### Notas de Implementación

- Los precios se negocian con tiradas de dados (2d6 + modificadores)
- La trazabilidad se pierde automáticamente al vender en planetas no adscritos al Convenio
- Los pedidos "in_transit" consumen espacio de almacén de la nave
- El límite de 25 pedidos por área previene spam y mantiene jugabilidad

---

## Tabla: `employee_tasks`

La tabla `employee_tasks` gestiona la cola de trabajo del Director Gerente y otros empleados, principalmente para búsquedas de personal.

### Esquema de la Tabla

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | Clave primaria |
| `game_id` | VARCHAR | ID del juego |
| `employee_id` | INTEGER | FK a personnel.id (quien realiza la tarea) |
| `task_type` | VARCHAR | Tipo de tarea (ej: "hire_search") |
| `status` | VARCHAR | Estado: "pending", "in_progress", "completed", "failed" |
| `queue_position` | INTEGER | Posición en la cola (1, 2, 3...) |
| `task_data` | TEXT | JSON con parámetros de la tarea (puesto, salario...) |
| `result_data` | TEXT | JSON con resultados (dados, éxito/fallo) |
| `created_date` | VARCHAR | Fecha creación |
| `started_date` | VARCHAR | Fecha inicio |
| `completion_date` | VARCHAR | Fecha prevista finalización |
| `finished_date` | VARCHAR | Fecha real finalización |

---

**Última actualización**: 2026-01-20
**Versión del esquema**: v3.1 (Misiones + Comercio + Tareas de Empleado)
