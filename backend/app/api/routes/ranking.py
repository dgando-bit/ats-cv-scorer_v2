import os
import tempfile

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import (
    get_job_search_pipeline,
)
from app.models.ranking import (
    JobRankingResult,
)
from app.providers.exceptions import (
    UnknownLocationError,
)
from app.services.cv.cv_extractor import (
    CVExtractor,
)
from app.services.matching.job_search_pipeline import (
    JobSearchPipeline,
)
from app.utils.file_validation import (
    read_valid_pdf,
)


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
        content = await read_valid_pdf(
            file
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:
            temp_file.write(
                content
            )

            temp_path = (
                temp_file.name
            )

        # cv_extractor.extract() et pipeline.search_and_rank()
        # sont entièrement synchrones/bloquants (parsing PDF,
        # appels HTTP France Travail/Groq, encodage sentence-
        # transformers). Les exécuter directement dans une route
        # "async def" gèlerait l'event loop unique du process
        # pendant toute la durée du pipeline, bloquant du même
        # coup toutes les autres requêtes (autocomplétion,
        # /health, autres utilisateurs). On les déporte donc
        # dans le threadpool de Starlette.
        cv = await run_in_threadpool(
            cv_extractor.extract,
            temp_path,
        )

        try:
            return await run_in_threadpool(
                pipeline.search_and_rank,
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

        except UnknownLocationError as exc:
            invalid_location = str(
                exc
            ).strip()

            raise HTTPException(
                status_code=422,
                detail={
                    "code": "unknown_location",
                    "message": (
                        "Localisation inconnue. "
                        "Vérifiez l'orthographe "
                        "ou sélectionnez une ville "
                        "dans la liste."
                    ),
                    "location": (
                        invalid_location
                    ),
                },
            ) from exc

    finally:
        if (
            temp_path
            and os.path.exists(
                temp_path
            )
        ):
            os.remove(
                temp_path
            )