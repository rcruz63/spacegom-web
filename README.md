# Spacegom Companion - Panel de Control Espacial

![Spacegom](https://img.shields.io/badge/Spacegom-Companion-00f3ff?style=for-the-badge)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-3D72D7?style=for-the-badge&logo=htmx&logoColor=white)

Aplicación web companion para el juego de mesa/rol **Spacegom**. Sustituye el soporte físico de papel y lápiz con un panel interactivo estilo "Spacecraft Control Panel" con estética cyberpunk/espacial.

## 🌌 Características

### 🚀 Setup de Partida
- **Identificación de Compañía y Nave**: Nombres personalizables con sugerencias aleatorias
- **Determinación de Área**: Tirada de 2d6 para determinar el área espacial (2-12)
- **Densidad de Mundos**: Tirada de 2d6 con clasificación automática (Baja/Media/Alta)
- **Posición Inicial**: Determinación de cuadrante inicial (grid 6x6)
- **Planeta de Origen**:
  - Tirada de 3d6 para código de planeta (111-666)
  - **Validación Automática**: Verifica requisitos de inicio (tecnología, población, convenio, soporte vital, productos)
  - **Búsqueda Consecutiva**: Si el planeta no es apto, busca el siguiente código secuencial automáticamente (111 → 112 → 113...)
  - Actualización de datos faltantes desde el mismo setup
- **Nave Inicial Bloqueada**: Para nuevas aventuras (herencia), la nave es siempre **Basic Starfall**

### 🎯 HUD Superior - Estado Crítico
- **Reserva de Combustible**: Indicador visual animado (0-30 unidades)
- **Capacidad de Carga de la Nave**: Monitor de bodega (40 UCN para Basic Starfall)
- **Almacén de la Compañía**: Depósito de mercancías en el planeta base (capacidad por definir)
- **Sistema de Daños**: Tres niveles (Leves, Moderados, Graves)
  - Alerta crítica "HIPERSALTO DESTRUIDO" en daños graves
  - Progresión: Leve (3) → Moderado (2) → Grave (2)
- **Calendario de Campaña**: Seguimiento de meses con **35 días por mes**
- **Reputación**: Rango dinámico de **-5 a +5** con codificación por colores

### 🗺️ Vista de Cuadrante - Navegación
- **Grid Interactivo 6x6**: Representa el área de exploración
- **Niebla de Guerra**: Cuadrantes sombreados hasta ser explorados
- **Marcador de Posición**: Indicador visual de la ubicación actual de la nave
- **Información Planetaria**: Panel lateral con detalles al seleccionar planetas
  - Soporte Vital (ej. RF - Respirador con filtraje)
  - Calidad del Espaciopuerto
  - Instalaciones Orbitales (Centro de cartografía, Academia, etc.)
  - Productos disponibles

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

- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: HTML + TailwindCSS + HTMX
- **Base de Datos**: SQLite (216 planetas importados)
- **Persistencia**: JSON para estado del juego
- **Fonts**: Orbitron, Share Tech Mono (Google Fonts)
- **Interactividad**: JavaScript vanilla para lógica de juego
- **Package Manager**: uv

## 📦 Instalación y Uso

### Requisitos Previos
- Python 3.12+
- uv (gestor de paquetes): `pip install uv`

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
source .venv/bin/activate
uvicorn main:app --app-dir app --reload --port 8000

# Opción 2: Scripting con uv
uv run uvicorn main:app --app-dir app --reload
```

La aplicación estará disponible en: `http://localhost:8000`

### Acceder a la Aplicación

1. **Página principal**: `http://localhost:8000/`
2. **Nueva Partida**: `http://localhost:8000/setup`
3. **Panel de Control**: `http://localhost:8000/dashboard`

## 🎮 Uso del Panel de Control

### Setup Inicial
1. **Identificación**: Introduce los nombres de tu compañía y nave (o usa las sugerencias)
2. **Área y Densidad**: El sistema tira automáticamente 2d6 para determinar el área y densidad
3. **Posición**: Se determina tu cuadrante inicial en el grid 6x6
4. **Planeta**: Tira 3d6 para tu planeta de origen
   - Si no es apto, el sistema buscará automáticamente el siguiente código válido
   - Completa datos faltantes si es necesario
5. **Finalizar**: Accede al dashboard para comenzar tu aventura

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

### Terminal Comercial
- Ajusta modificadores de precio según negociación
- Botones de COMPRAR/VENDER para transacciones
- Resumen financiero en tiempo real

## 📁 Estructura del Proyecto

```
spacegom-web/
├── app/
│   ├── main.py              # FastAPI app y API endpoints
│   ├── game_state.py        # Lógica de persistencia del estado
│   ├── ship_data.py         # Modelos de naves y estadísticas
│   ├── dice.py              # Utilidades de dados
│   ├── database.py          # Modelos SQLAlchemy
│   ├── import_planets.py    # Script de importación de datos
│   └── templates/
│       ├── base.html        # Template base con estilos
│       ├── index.html       # Página de inicio
│       ├── setup.html       # Setup de nueva partida
│       └── dashboard.html   # Panel de control principal
├── data/
│   ├── spacegom.db          # Base de datos SQLite
│   ├── Base_de_datos_de_planetas.xlsx
│   └── games/               # Estados guardados
├── files/                   # Materiales de referencia del juego y archivos de datos
│   ├── Calendario_de_Campana.pdf
│   ├── Ficha_de_Compania.pdf
│   ├── Hoja_de_Mundos.pdf
│   ├── Tesoreria.pdf
│   ├── nombres_megacorp.csv    # 470 nombres de compañías
│   ├── nombres_naves.csv       # 500 nombres de naves
│   └── nombres_personal.csv    # 1000 nombres de personal
├── pyproject.toml
├── README.md
├── API.md                   # Documentación de la API
├── DATABASE.md              # Documentación de la base de datos
└── CONTEXT.md               # Contexto del proyecto
```

## 📚 Documentación de Referencia

El proyecto incluye materiales originales del juego de mesa en la carpeta `files/`:

### Documentos PDF
- **Calendario de Campaña**: Sistema de 35 días por mes
- **Ficha de Compañía**: Plantilla oficial para gestión de empresa
- **Hoja de Mundos**: Listado completo de planetas con códigos 3d6
- **Tesorería**: Control financiero detallado
- **Pack Completo**: Todos los descargables del juego

### Archivos CSV de Nombres
- **nombres_megacorp.csv**: 470 nombres de megacorporaciones
- **nombres_naves.csv**: 500 nombres de naves espaciales inspirados en ficción, historia y mitología
- **nombres_personal.csv**: 1000 nombres de personal para futura gestión de tripulación

## 🔮 Próximas Mejoras

- [ ] Sistema de eventos aleatorios (diarios/de viaje)
- [ ] Sistema de combate espacial
- [ ] Calendario dinámico con meses de 35 días
- [ ] Mejora y reparación de naves en astilleros
- [ ] Sistema de misiones y contratos procedurales
- [ ] Gestión detallada de carga (peso/volumen)
- [ ] Modo multijugador
- [ ] Generación procedural de planetas adicionales
- [ ] Gráficos de estadísticas y progreso
- [ ] Exportación de partidas a PDF

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
- Colores personalizados en las clases de Tailwind
- Estilos CSS adicionales en la sección `<style>`
- Variables de color neón

### Importar Datos de Planetas

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar script de importación
python -m app.import_planets
```

## 📖 Documentación Adicional

Para más información sobre el proyecto:

- **[API.md](API.md)**: Documentación completa de todos los endpoints de la API REST
- **[DATABASE.md](DATABASE.md)**: Esquema detallado de la base de datos, campos de la tabla `planets`, ejemplos y consultas útiles
- **[CONTEXT.md](CONTEXT.md)**: Contexto del proyecto, decisiones de diseño y próximos pasos

## 📝 Licencia

[Especifica tu licencia aquí]

## 👨‍🚀 Créditos

Desarrollado para la comunidad de Spacegom.

**Mecánicas de juego** basadas en el manual oficial de Spacegom.

---

**¡Que tengas un buen viaje, Comandante!** 🚀
