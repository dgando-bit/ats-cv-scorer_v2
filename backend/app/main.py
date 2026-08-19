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

app.include_router(match_router)
app.include_router(job_router)
app.include_router(cv_router)
app.include_router(analyze_router)
app.include_router(jobs.router)
app.include_router(ranking_router)