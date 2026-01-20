# Usamos la imagen oficial de uv con Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Configuración de entorno para Python y uv
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Directorio de trabajo en el contenedor
WORKDIR /app

# 1. Copiamos solo los ficheros de dependencias primero (para aprovechar caché de Docker)
COPY pyproject.toml uv.lock* ./

# 2. Instalamos las dependencias
# --no-dev: para producción (puedes quitarlo si quieres herramientas de dev)
# --no-root: no instalamos el proyecto en sí todavía, solo librerías
RUN uv sync --frozen --no-install-project --no-dev

# 3. Copiamos el resto del código
COPY . .

# 4. Instalamos el proyecto actual
RUN uv sync --frozen --no-dev

# Exponemos el puerto
EXPOSE 8000

# El comando de arranque usando el entorno virtual gestionado por uv
# Nota: uv crea el venv en .venv por defecto dentro del workdir
CMD ["/app/.venv/bin/uvicorn", "main:app", "--app-dir", "app", "--host", "0.0.0.0", "--port", "8000"]