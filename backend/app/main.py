from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.match import router as match_router
from app.api.routes.job import router as job_router
from app.api.routes.cv import router as cv_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes import jobs
from app.api.routes.ranking import (
    router as ranking_router,
)
from app.api.routes.locations import (
    router as locations_router,
)
from app.api.dependencies import (
    get_semantic_service,
    get_relevance_evaluator,
    get_requirements_batch_extractor,
    get_job_provider,
    get_job_search_pipeline,
)

app = FastAPI(
    title="ATS CV Scorer",
    description="CV parsing and ATS scoring API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ats-frontend-821673292315.europe-west1.run.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ats-cv-scorer_v2",
    }


@app.on_event("startup")
def warm_up_singletons() -> None:
    """
    Précharge les singletons coûteux (modèle sémantique,
    clients Groq, provider France Travail) au démarrage du
    conteneur plutôt qu'à la première requête utilisateur.

    Sans ça, la toute première requête /api/jobs/rank paie le
    coût cumulé du chargement du modèle sentence-transformers
    et de la première connexion à chaque service externe.
    """
    print(
        "[startup] Préchauffage des services...",
        flush=True,
    )

    get_semantic_service()
    get_relevance_evaluator()
    get_requirements_batch_extractor()
    get_job_provider()
    get_job_search_pipeline()

    print(
        "[startup] Préchauffage terminé.",
        flush=True,
    )

app.include_router(match_router)
app.include_router(job_router)
app.include_router(cv_router)
app.include_router(analyze_router)
app.include_router(jobs.router)
app.include_router(ranking_router)
app.include_router(locations_router)
