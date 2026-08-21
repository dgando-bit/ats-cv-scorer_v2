import os
import tempfile

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)

from app.api.dependencies import (
    get_cv_extractor,
)
from app.models.cv import CV
from app.services.cv.cv_extractor import (
    CVExtractor,
)
from app.utils.file_validation import (
    read_valid_pdf,
)


router = APIRouter(
    prefix="/api/cv",
    tags=["cv"],
)


@router.post(
    "/extract",
    response_model=CV,
)
async def extract_cv(
    file: UploadFile = File(...),
    extractor: CVExtractor = Depends(
        get_cv_extractor
    ),
) -> CV:
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

        return extractor.extract(
            temp_path
        )

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