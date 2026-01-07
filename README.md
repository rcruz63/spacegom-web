# Spacegom Companion - Panel de Control Espacial

![Spacegom](https://img.shields.io/badge/Spacegom-Companion-00f3ff?style=for-the-badge)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-3D72D7?style=for-the-badge&logo=htmx&logoColor=white)

Aplicación web companion para el juego de mesa/rol **Spacegom**. Sustituye el soporte físico de papel y lápiz con un panel interactivo estilo "Spacecraft Control Panel" con estética cyberpunk/espacial.

## 🌌 Características

### 🎯 HUD Superior - Estado Crítico
- **Reserva de Combustible**: Indicador visual animado (0-30 unidades)
- **Capacidad del Almacén**: Monitor de carga (máximo 40 UCN)
- **Sistema de Daños**: Tres niveles (Leves, Moderados, Graves)
  - Alerta crítica "HIPERSALTO DESTRUIDO" en daños graves
- **Calendario de Campaña**: Seguimiento de meses (1-12)
- **Reputación**: Rango dinámico de -5 a +5 con codificación por colores

### 🗺️ Vista de Cuadrante - Navegación
- **Grid Interactivo 6x6**: Representa el área de exploración
- **Niebla de Guerra**: Cuadrantes sombreados hasta ser explorados
- **Información Planetaria**: Panel lateral con detalles al seleccionar planetas
  - Soporte Vital (ej. RF - Respirador con filtraje)
  - Calidad del Espaciopuerto
  - Instalaciones Orbitales (Centro de cartografía, Academia, etc.)

### 👥 Gestión de Tripulación - Bio-Métricas
- **Tarjetas de Tripulantes**:
  - Puesto y Nombre
  - Salario (SC)
  - Experiencia: Novato / Estándar / Veterano
  - Indicador de Moral: Baja / Media / Alta
- **Monitor de Salubridad**: Indicador de riesgos para la tripulación

### 💰 Terminal Comercial y Tesorería
- **Tabla de Compraventa de Mercancías**:
  - Modificadores de precio dinámicos (x0.8, x1.0, x1.2)
  - Basado en habilidades del Negociador
- **Resumen Financiero**:
  - Tesorería actual
  - Gastos semanales (salarios, mantenimiento)
  - Préstamos mensuales

## 🎨 Estética Visual

- **Paleta de Colores**: Dark mode con slate-950 como base
- **Bordes Neón**: Cyan (#00f3ff) y verde neón (#00ff9d)
- **Tipografía Técnica**:
  - `Orbitron`: Títulos y displays numéricos
  - `Share Tech Mono`: Texto técnico y monoespaciado
- **Efectos Visuales**:
  - Glassmorphism para paneles
  - Gradientes dinámicos
  - Animaciones suaves en interacciones
  - Background grid de estilo terminal espacial

## 🚀 Tecnologías

- **Backend**: FastAPI (Python)
- **Frontend**: HTML + TailwindCSS + HTMX
- **Fonts**: Orbitron, Share Tech Mono (Google Fonts)
- **Interactividad**: JavaScript vanilla para lógica de juego

## 📦 Instalación y Uso

### Requisitos Previos
- Python 3.11+
- uv (gestor de paquetes)

### Instalación

```bash
# Clonar el repositorio (si aplica)
git clone <tu-repositorio>
cd spacegom-web

# Instalar dependencias con uv
uv sync
```

### Ejecutar la Aplicación

```bash
# Opción 1: Usando uvicorn directamente
uv run uvicorn app.main:app --reload

# Opción 2: Usando el script run.py
uv run python app/run.py
```

La aplicación estará disponible en: `http://localhost:8000`

### Acceder al Dashboard

1. Página principal: `http://localhost:8000/`
2. Panel de Control: `http://localhost:8000/dashboard`

## 🎮 Uso del Panel de Control

### HUD Superior
- **Combustible/Almacén**: Usa los botones `+/-` para ajustar valores
- **Daños**: Haz clic en los indicadores para activar/desactivar
- **Calendario/Reputación**: Usa las flechas `◄►` para navegar

### Vista de Cuadrante
- Haz clic en cualquier cuadrante para explorarlo
- La niebla de guerra se disipa al explorar
- Los planetas muestran información detallada al seleccionarlos

### Tripulación
- Visualiza el estado de cada miembro
- Monitor de salubridad general
- Botón para reclutar nuevos tripulantes

### Terminal Comercial
- Ajusta modificadores de precio según negociación
- Botones de COMPRAR/VENDER para transacciones
- Resumen financiero en tiempo real

## 📁 Estructura del Proyecto

```
spacegom-web/
├── app/
│   ├── main.py              # FastAPI app y rutas
│   ├── models.py            # Modelos de datos
│   ├── run.py               # Script de ejecución
│   └── templates/
│       ├── base.html        # Template base con estilos
│       ├── index.html       # Página de inicio
│       ├── dashboard.html   # Panel de control principal
│       └── components/      # Componentes reutilizables
├── pyproject.toml
└── README.md
```

## 🔮 Próximas Mejoras

- [ ] Persistencia de datos (SQLite/PostgreSQL)
- [ ] Sistema de guardado/carga de partidas
- [ ] Modo multijugador
- [ ] Generación procedural de planetas
- [ ] Sistema de misiones y eventos aleatorios
- [ ] Integración con backend Python para lógica compleja
- [ ] Sistema de combate espacial
- [ ] Gráficos de estadísticas y progreso

## 🛠️ Desarrollo

### Agregar Nuevas Rutas

Edita `app/main.py`:

```python
@app.get("/nueva-ruta")
async def nueva_ruta(request: Request):
    return templates.TemplateResponse("tu_template.html", {"request": request})
```

### Personalizar Estilos

Los estilos base están en `app/templates/base.html`. Puedes modificar:
- Colores personalizados en `tailwind.config`
- Estilos CSS adicionales en la sección `<style>`
- Variables de color neón

## 📝 Licencia

[Especifica tu licencia aquí]

## 👨‍🚀 Créditos

Desarrollado para la comunidad de Spacegom.

---

**¡Que tengas un buen viaje, Comandante!** 🚀
