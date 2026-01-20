# import_planets.py - Importación de Datos de Planetas

## Overview

Script para importar planetas desde archivo Excel simplificado a la base de datos SQLite. Parsea campos complejos como espaciopuerto y maneja validación de datos.

**Ubicación**: `app/import_planets.py`
**Líneas**: 200
**Dependencias**: `pandas`, `database`

## Función parse_spaceport(spaceport_str: str) -> dict

Parsea código de espaciopuerto en componentes.

**Formato**: "XXX-ZZ-N"
- XXX: Calidad (EXC, NOT, MED, BAS, RUD, SIN)
- ZZ: Densidad de combustible (DB, DM, DA, N)
- N: Precio de amarre

**Retorno**: `{"quality": str, "fuel_density": str, "docking_price": int}`

## Función parse_boolean(value, true_values=['X', 'SÍ', 'SI', 'YES', '1', 'TRUE']) -> bool

Convierte valor a booleano con lista configurable de valores verdaderos.

## Función import_planets_from_excel(excel_path: str)

Importa planetas desde Excel a base de datos.

### Proceso
1. Inicializa base de datos
2. Lee archivo Excel con pandas
3. Limpia nombres de columnas
4. Elimina planetas existentes (no custom)
5. Para cada fila:
   - Parsea código (o calcula desde índice)
   - Parsea espaciopuerto
   - Crea objeto Planet con todos los campos
   - Agrega a sesión
6. Commit y muestra estadísticas

### Campos Mapeados
- **Identificación**: code, name
- **Soporte Vital**: life_support, local_contagion_risk, days_to_hyperspace, legal_order_threshold
- **Espaciopuerto**: spaceport_quality, fuel_density, docking_price (parsed)
- **Instalaciones**: orbital_cartography_center, orbital_hackers, etc.
- **Productos**: product_indu, product_basi, etc. (boolean)
- **Comercio**: self_sufficiency_level, ucn_per_order, max_passengers, mission_threshold
- **Validación**: convenio_spacegom (tech_level y population_over_1000 se llenan después)

## Ejecución

```bash
python -m app.import_planets
```

O directamente:
```bash
python app/import_planets.py
```

## Dependencias

- **pandas**: Lectura de Excel
- **database**: Modelos SQLAlchemy

## Notas de Implementación

- **Manejo de Errores**: Rollback en caso de excepción
- **Validación**: Códigos de planeta válidos (111-666)
- **Flexibilidad**: Maneja formatos variables en Excel
- **Limpieza**: Elimina planetas no custom antes de importar

## Mejores Prácticas

- Ejecutar en entorno de desarrollo
- Verificar archivo Excel antes de importar
- Hacer backup de base de datos si necesario
- Revisar logs de importación para errores