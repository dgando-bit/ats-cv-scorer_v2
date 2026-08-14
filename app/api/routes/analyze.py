import os
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.match import MatchResult
from app.services.cv_extractor import CVExtractor
from app.services.job_offer_extractor import JobOfferExtractor
from app.services.matching_engine import MatchingEngine


router = APIRouter(
    prefix="/api",
    tags=["analysis"],
)

cv_extractor = CVExtractor()
job_offer_extractor = JobOfferExtractor()
matching_engine = MatchingEngine()


@router.post(
    "/analyze",
    response_model=MatchResult,
)
async def analyze(
    file: UploadFile = File(...),
    job_text: str = Form(...),
    job_title: str | None = Form(None),
    company: str | None = Form(None),
    location: str | None = Form(None),
    contract_type: str | None = Form(None),
) -> MatchResult:

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:

            content = await file.read()
            temp_file.write(content)

            temp_path = temp_file.name

        cv = cv_extractor.extract(
            temp_path
        )

        job = job_offer_extractor.extract(
            job_text,
            title=job_title,
            company=company,
            location=location,
            contract_type=contract_type,
        )

        return matching_engine.match(
            cv,
            job,
        )

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)