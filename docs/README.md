# Documentación del Proyecto Spacegom-web

Esta documentación cubre todos los archivos fuente del proyecto Spacegom-web, un panel de control web para el juego de mesa Spacegom.

## Índice de Módulos

### Backend (Python)
- [main.py](main.md) - API principal de FastAPI con todos los endpoints
- [game_state.py](game_state.md) - Gestión del estado persistente del juego
- [database.py](database.md) - Modelos SQLAlchemy y conexión a BD
- [dice.py](dice.md) - Utilidades de tiradas de dados
- [ship_data.py](ship_data.md) - Modelos de naves y estadísticas
- [import_planets.py](import_planets.md) - Script de importación de datos de planetas
- [event_handlers.py](event_handlers.md) - Manejo de eventos del juego
- [event_logger.py](event_logger.md) - Logging de eventos
- [models.py](models.md) - Modelos de datos adicionales
- [name_suggestions.py](name_suggestions.md) - Sugerencias de nombres para compañías y naves
- [personnel_manager.py](personnel_manager.md) - Gestión de personal y empleados
- [run.py](run.md) - Script de ejecución principal
- [time_manager.py](time_manager.md) - Gestión del tiempo y calendario
- [trade_manager.py](trade_manager.md) - Lógica de comercio y transacciones
- [update_planets_from_excel.py](update_planets_from_excel.md) - Actualización de planetas desde Excel
- [utils.py](utils.md) - Utilidades generales

### Frontend (JavaScript)
- [dice-roller.js](dice-roller.md) - Lógica JavaScript para tiradas de dados
- [passenger_transport.js](passenger_transport.md) - Gestión de transporte de pasajeros

### Templates (HTML)
- [base.html](base.md) - Template base con estilos
- [dashboard.html](dashboard.md) - Panel de control principal
- [index.html](index.md) - Página de inicio
- [setup.html](setup.md) - Setup de nueva partida
- [logs.html](logs.md) - Página de logs
- [missions.html](missions.md) - Gestión de misiones
- [personnel.html](personnel.md) - Gestión de personal
- [trade.html](trade.md) - Terminal comercial
- [treasury.html](treasury.md) - Tesorería y finanzas

### Componentes (HTML)
- [dice_result.html](dice_result.md) - Componente de resultados de dados
- [dice_widget.html](dice_widget.md) - Widget de dados

## Arquitectura General

El proyecto sigue una arquitectura web típica con FastAPI como backend, SQLite como base de datos, y HTML/JS con HTMX para el frontend.

### Flujo Principal
1. **Setup**: Creación de partida con configuración inicial
2. **Dashboard**: Panel principal con HUD y navegación
3. **Acciones**: Gestión de personal, comercio, misiones, etc.
4. **Eventos**: Sistema de tiempo y eventos automáticos

### Dependencias Clave
- FastAPI para API REST
- SQLAlchemy para ORM
- Jinja2 para templates
- HTMX para interacciones dinámicas
- TailwindCSS para estilos

## Cómo Usar Esta Documentación

Cada archivo fuente tiene su propia página de documentación con:
- **Overview**: Propósito y rol en el proyecto
- **Funciones/Clases**: Lista detallada con parámetros y retornos
- **Dependencias**: Módulos importados y relaciones
- **Notas**: Lógica compleja y mejores prácticas

Para contribuir, lee la documentación del módulo relevante antes de hacer cambios.