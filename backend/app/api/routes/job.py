from fastapi import APIRouter
from pydantic import BaseModel

from app.models.job import JobOffer
from app.services.jobs.job_offer_extractor import JobOfferExtractor


router = APIRouter(
    prefix="/api/job",
    tags=["job"],
)


class JobExtractRequest(BaseModel):
    text: str
    title: str | None = None
    company: str | None = None
    location: str | None = None
    contract_type: str | None = None


job_offer_extractor = JobOfferExtractor()


@router.post(
    "/extract",
    response_model=JobOffer,
)
def extract_job_offer(
    payload: JobExtractRequest,
) -> JobOffer:

    return job_offer_extractor.extract(
        payload.text,
        title=payload.title,
        company=payload.company,
        location=payload.location,
        contract_type=payload.contract_type,
    )