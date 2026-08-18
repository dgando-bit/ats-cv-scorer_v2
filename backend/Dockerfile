# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Dépendances système utiles notamment pour certains traitements PDF
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Installer les dépendances avant de copier le code
# => meilleur usage du cache Docker
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Copier l'application
COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]