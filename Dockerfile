# --- ETAPA 1: 'builder' ---
# Esta etapa solo instala las dependencias en un virtualenv
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

# Habilitar compilación de bytecode
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Crear el entorno virtual
RUN uv venv .venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar solo los archivos de dependencia
COPY uv.lock pyproject.toml ./

# Instalar solo las dependencias (sin el proyecto)
# Esto crea una capa de Docker que solo se invalida si las dependencias cambian
RUN uv sync --frozen --no-install-project --no-dev


# --- ETAPA 2: 'final' ---
# Esta es la imagen final que se ejecutará
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Copiar el entorno virtual con las dependencias ya instaladas desde la etapa 'builder'
COPY --from=builder /app/.venv /app/.venv

# Copiar todo el código fuente del proyecto
ADD . /app

# Configurar el PATH para usar el virtualenv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Instalar el proyecto en sí (las dependencias ya están en el venv)
RUN uv sync --frozen --no-dev

# Comando para ejecutar la aplicación
CMD ["uv", "run", "main.py"]