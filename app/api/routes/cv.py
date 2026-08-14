import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.cv import CV
from app.services.cv_extractor import CVExtractor


router = APIRouter(
    prefix="/api/cv",
    tags=["cv"],
)


cv_extractor = CVExtractor()


@router.post(
    "/extract",
    response_model=CV,
)
async def extract_cv(
    file: UploadFile = File(...),
) -> CV:

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    suffix = ".pdf"

    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            content = await file.read()

            temp_file.write(content)

            temp_path = temp_file.name

        return cv_extractor.extract(
            temp_path
        )

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)