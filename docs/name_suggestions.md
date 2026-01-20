# name_suggestions.py - Sugerencias de Nombres

## Overview

Utilidades para cargar y servir nombres aleatorios desde archivos CSV. Proporciona sugerencias para compañías, naves y personal.

**Ubicación**: `app/name_suggestions.py`
**Líneas**: 107
**Dependencias**: `csv`, `random`, `pathlib`

## Archivos CSV

- `files/nombres_personal.csv`: Nombres de personal (1000 entradas)
- `files/nombres_megacorp.csv`: Nombres de compañías (470 entradas)
- `files/nombres_naves.csv`: Nombres de naves (500 entradas)

## Función load_names_from_csv(csv_path: Path) -> List[str]

Carga nombres desde archivo CSV.

**Formato CSV**: ID,Nombre
**Retorno**: Lista de nombres de la segunda columna

## Funciones de Sugerencia

### get_random_personal_name() -> str
Retorna nombre personal aleatorio con cache.

### get_random_company_name() -> str
Retorna nombre de compañía aleatorio con cache.

### get_random_ship_name() -> str
Retorna nombre de nave aleatorio con cache.

## Función reload_names()

Recarga todos los nombres desde archivos CSV. Útil si se modifican en runtime.

## Cache

Usa variables globales para cache de nombres cargados, evitando recargas innecesarias.

## Dependencias

- **csv**: Lectura de archivos CSV
- **random**: Selección aleatoria
- **pathlib**: Manejo de rutas

## Notas de Implementación

- **Lazy Loading**: Carga nombres solo cuando se necesitan
- **Fallback**: Nombres por defecto si CSV no existe
- **Encoding**: UTF-8 para soporte de caracteres especiales
- **Error Handling**: Manejo de errores al leer CSV

## Mejores Prácticas

- Usar cache para performance
- Manejar errores gracefully
- Mantener CSVs actualizados
- Usar reload_names() para testing