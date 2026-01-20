FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Instalar dependencias
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev

# Copiar el código fuente
COPY . .

# Instalar el proyecto
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Comando por defecto (sobrescrito por docker-compose en desarrollo)
CMD ["/app/.venv/bin/uvicorn", "main:app", "--app-dir", "app", "--host", "0.0.0.0", "--port", "8000"]