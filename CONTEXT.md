# Spacegom Companion - Contexto de Proyecto

Este documento resume el estado actual del desarrollo para permitir la continuación del proyecto en sesiones futuras.

## Estado del Proyecto
Aplicación web tipo "Companion" para el juego Spacegom, desarrollada con FastAPI, Jinja2 y JavaScript/CSS moderno.

### Avances Realizados
1.  **Backend & Datos**:
    *   Importación de 216 planetas desde CSV a SQLite.
    *   Sistema de persistencia de partidas (`GameState`) en archivos JSON.
    *   Definición de modelos de naves y sus estadísticas en `app/ship_data.py`.
2.  **Dashboard**:
    *   HUD funcional: Combustible, Almacén, Calendario y Reputación.
    *   Cuadrícula de navegación (6x6) con fondo de estrellas generado por CSS.
    *   Historial de Mundos (Archivos Estelares) que permite ver detalles de planetas descubiertos.
    *   Mapeo único de planetas: Cada mundo se "ancla" a un cuadrante específico por partida.
3.  **Lógica de Juego**:
    *   Implementación de localizaciones en el planeta (Mundo, Puerto, Orbital, Estación).
    *   Lógica de navegación entre Áreas (Columnas A <-> F) respetando límites.

## Pendientes y Problemas Identificados (Setup Inicial)

### 1. Modelo de Nave
*   **Problema**: Actualmente el setup permite elegir cualquier modelo.
*   **Requerimiento**: Para el inicio de la aventura (herencia), la nave debe ser fija al modelo **Basic Starfall**.

### 2. Lógica del Planeta Inicial
*   **Problema de búsqueda**: Si el planeta no es válido (ej: Sin atmósfera o tecnología muy baja), el sistema pide volver a tirar.
*   **Manual**: Según las reglas, si el planeta tirado no es apto, se debe consultar el **siguiente código consecutivo** (ej: 111 -> 112 -> 113...) hasta encontrar uno válido, en lugar de una tirada nueva.
*   **Fuga de datos (Leak)**: Durante el setup, los valores de "Nivel tecnológico" y "Población" introducidos manualmente para un planeta inválido persisten en la interfaz al consultar el siguiente código, causando confusión.
*   **Planetas Fantasma**: Se ha detectado que a veces, tras varios intentos fallidos, el planeta anterior queda registrado en el cuadrante o en el log. **Solo debe existir el planeta final válido** y cualquier dato previo de planetas descartados debe ser borrado del `GameState`.

## Estructura de Archivos Clave
*   `app/main.py`: Endpoints de la API y rutas.
*   `app/game_state.py`: Lógica de persistencia y métodos de descubrimiento/navegación.
*   `app/ship_data.py`: Tabla de naves y sugeridores de nombres.
*   `app/templates/dashboard.html`: Interfaz principal y lógica JS del HUD/Grid.
*   `app/templates/setup.html`: Proceso de creación de partida (donde residen los bugs mencionados).

## Decisiones de Diseño
*   **Aesthetics**: Se ha mantenido una estética "Retro-Futurista / Neon-Blue" con micro-animaciones en el grid.
*   **Navegación**: Los planetas se identifican por sus códigos de 3 dígitos (111-666).
*   **Persistencia**: Se usa una carpeta `data/games/{game_id}/` para separar los datos de cada partida.

---
*Contexto generado el 2026-01-08 para relevo en desarrollo.*
