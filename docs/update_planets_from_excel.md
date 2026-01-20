# update_planets_from_excel.py - Actualización de Planetas desde Excel

## Overview

Script para actualizar planetas desde archivo Excel SIN eliminar datos existentes. Preserva campos modificados durante el juego.

**Ubicación**: `app/update_planets_from_excel.py`
**Líneas**: 198
**Dependencias**: `pandas`, `database`, `import_planets`

## Función update_planets_from_excel(excel_path: str)

Actualiza planetas desde Excel preservando datos existentes.

### Campos Actualizados
- **Identificación**: name
- **Soporte Vital**: life_support, local_contagion_risk, days_to_hyperspace, legal_order_threshold
- **Espaciopuerto**: spaceport_quality, fuel_density, docking_price (parsed)
- **Instalaciones**: orbital_cartography_center, orbital_hackers, etc.
- **Productos**: product_indu, product_basi, etc.
- **Comercio**: self_sufficiency_level, ucn_per_order, max_passengers, mission_threshold
- **Convenio**: convenio_spacegom

### Campos Preservados
- **tech_level**: Nivel tecnológico (seteado en setup)
- **population_over_1000**: Población (seteado en setup)
- **notes**: Notas del usuario
- **is_custom**: Flag de planetas custom

### Lógica
1. Lee Excel con pandas
2. Para cada fila:
   - Si planeta existe: actualiza campos del Excel
   - Si no existe: crea nuevo planeta
3. Commit y muestra estadísticas

## Dependencias

- **pandas**: Lectura de Excel
- **database**: Modelos Planet
- **import_planets**: Funciones parse_spaceport, parse_boolean

## Notas de Implementación

- **Safe Update**: No elimina datos existentes
- **Preservation**: Mantiene customizaciones del usuario
- **Validation**: Maneja códigos inválidos
- **Rollback**: En caso de error

## Mejores Prácticas

- Ejecutar después de cambios en Excel
- Hacer backup antes de actualizar
- Verificar campos preservados
- Usar para actualizaciones incrementales