# utils.py - Utilidades Generales

## Overview

Funciones de utilidad para decodificación de códigos del juego y formateo de datos.

**Ubicación**: `app/utils.py`
**Líneas**: 109
**Dependencias**: Ninguna

## Diccionarios de Decodificación

### LIFE_SUPPORT_DESCRIPTIONS
Mapea códigos de soporte vital a descripciones legibles.

### TECH_LEVEL_DESCRIPTIONS
Mapea códigos de nivel tecnológico a descripciones.

### SPACEPORT_QUALITY
Mapea códigos de calidad de espaciopuerto a descripciones.

### FUEL_DENSITY
Mapea códigos de densidad de combustible a descripciones.

## Funciones

### decode_life_support(code: str) -> str
Decodifica código de soporte vital a texto legible.

### decode_tech_level(code: str) -> str
Decodifica nivel tecnológico a texto legible.

### parse_spaceport(spaceport_str: str) -> dict
Parsea string de espaciopuerto en componentes detallados.

**Retorno**:
```python
{
    "quality": str,      # Descripción legible
    "quality_code": str, # Código original
    "fuel": str,         # Descripción de combustible
    "fuel_code": str,    # Código de combustible
    "price": int         # Precio de amarre
}
```

### format_game_date(day: int, month: int, year: int) -> str
Formatea fecha del juego en "dd-mm-yyyy".

## Notas de Implementación

- **Decodificación**: Convierte códigos internos a texto legible para UI
- **Parsing Seguro**: Maneja formatos inválidos gracefully
- **Fallback**: Retorna código original si no hay descripción
- **Consistencia**: Usado en format_planet_data

## Mejores Prácticas

- Mantener diccionarios actualizados con reglas del juego
- Usar en respuestas API para mejorar UX
- Manejar casos edge en parsing
- Centralizar lógica de formateo