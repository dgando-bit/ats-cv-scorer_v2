from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_job_provider
from app.models.job import JobOffer
from app.providers.base import JobProvider


router = APIRouter(
    prefix="/api/jobs",
    tags=["jobs"],
)


@router.get(
    "/search",
    response_model=list[JobOffer],
)
def search_jobs(
    keywords: str = Query(..., min_length=2),
    location: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    provider: JobProvider = Depends(get_job_provider),
) -> list[JobOffer]:

    return provider.search_jobs(
        keywords=keywords,
        location=location,
        limit=limit,
    )