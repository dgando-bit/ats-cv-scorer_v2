import os
import tempfile

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)

from app.api.dependencies import (
    get_job_search_pipeline,
)
from app.models.ranking import JobRankingResult
from app.services.cv.cv_extractor import CVExtractor
from app.services.matching.job_search_pipeline import (
    JobSearchPipeline,
)
from app.utils.file_validation import read_valid_pdf


router = APIRouter(
    prefix="/api/jobs",
    tags=["jobs"],
)

cv_extractor = CVExtractor()


@router.post(
    "/rank",
    response_model=JobRankingResult,
)
async def rank_jobs(
    file: UploadFile = File(...),
    keywords: str = Form(...),
    location: str | None = Form(None),
    insee_code: str | None = Form(None),
    limit: int = Form(10),
    pipeline: JobSearchPipeline = Depends(
        get_job_search_pipeline
    ),
) -> JobRankingResult:
    temp_path: str | None = None

    try:
        content = await read_valid_pdf(file)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        cv = cv_extractor.extract(
            temp_path
        )

        return pipeline.search_and_rank(
            cv=cv,
            keywords=keywords,
            location=location,
            insee_code=insee_code,
            provider_limit=max(
                50,
                limit,
            ),
            retrieval_top_k=max(
                20,
                limit,
            ),
            final_limit=limit,
        )

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)