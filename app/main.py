from fastapi import FastAPI


app = FastAPI(
    title="ATS CV Scorer",
    description="CV parsing and ATS scoring API",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ats-cv-scorer_v2",
    }