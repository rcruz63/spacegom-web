# ship_data.py - Modelos de Naves y Estadísticas

## Overview

Este módulo contiene datos estáticos de todos los modelos de naves disponibles en Spacegom, incluyendo estadísticas de combate, capacidad y costos.

**Ubicación**: `app/ship_data.py`
**Líneas**: 108
**Dependencias**: Ninguna

## Diccionario SHIP_MODELS

Contiene configuración completa de cada modelo de nave:

### Campos por Modelo
- `jump`: Capacidad de salto hiperespacial
- `passengers`: Capacidad máxima de pasajeros
- `storage`: Capacidad de almacenamiento en UCN
- `damage_support`: Puntos de daño por nivel (L=Leve, M=Moderado, G=Grave)
- `modifier`: Modificador general (para cálculos)
- `cost`: Costo en SC

### Modelos Disponibles
1. **Basic Starfall**: Nave básica inicial
2. **Spacegom Fortune**: Mayor almacenamiento
3. **Warehouse Ravana**: Nave de carga
4. **Long Explorer**: Mayor rango de salto
5. **Space Challenger**: Balanceado
6. **High Milkway**: Alta capacidad
7. **Fast Paladin Store**: Nave premium
8. **Tenacity triquadrant**: Alta durabilidad
9. **Defiant Navigator**: Nave avanzada
10. **Space Glory**: Nave máxima

## Sugerencias de Nombres

### COMPANY_NAME_SUGGESTIONS
Lista de nombres sugeridos para compañías.

### SHIP_NAME_SUGGESTIONS
Lista de nombres sugeridos para naves.

## Función get_ship_stats(model_name: str) -> dict

Retorna estadísticas de un modelo específico, con fallback a "Basic Starfall" si no existe.

## Notas de Implementación

- **Datos Estáticos**: No requiere base de datos
- **Fallback Seguro**: Siempre retorna datos válidos
- **Extensible**: Fácil agregar nuevos modelos
- **Validación**: Usar en setup para inicializar capacidades

## Mejores Prácticas

- Mantener consistencia en nombres de campos
- Actualizar costos según reglas del juego
- Usar `get_ship_stats()` para acceso seguro
- Validar modelo antes de usar estadísticas