# backend/Dockerfile
# syntax=docker/dockerfile:1

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

# Précharger le modèle sentence-transformers DANS l'image, au moment
# du build, plutôt que de le télécharger depuis Hugging Face Hub à
# chaque cold-start d'un nouveau conteneur Cloud Run. Le modèle est
# alors déjà présent sur disque quand le conteneur démarre : plus
# aucun appel réseau au préchauffage, juste du chargement mémoire
# local (rapide et prévisible).
#
# HF_TOKEN est passé via --mount=type=secret : monté uniquement le
# temps de cette commande, jamais écrit dans un layer ni dans
# l'historique de l'image. Ne jamais utiliser ARG/ENV pour un secret,
# ça le laisserait en clair dans l'image finale.
#
# Le nom du modèle doit rester identique à
# SemanticSimilarityService.MODEL_NAME dans
# app/services/semantic/semantic_similarity_service.py
RUN --mount=type=secret,id=hf_token \
    HF_TOKEN=$(cat /run/secrets/hf_token 2>/dev/null || echo "") \
    uv run python -c \
    "from sentence_transformers import SentenceTransformer; \
     SentenceTransformer('intfloat/multilingual-e5-small')"

# Copier l'application
COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]