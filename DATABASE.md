# Documentación de la Base de Datos

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

**Última actualización**: 2026-01-08  
**Versión del esquema**: v2.0 (Refactorizado)
