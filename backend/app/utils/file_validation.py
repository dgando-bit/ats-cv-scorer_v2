from fastapi import HTTPException, UploadFile


PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/octet-stream",
}


async def read_valid_pdf(
    file: UploadFile,
) -> bytes:

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    # Un vrai fichier PDF commence par %PDF-
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Only valid PDF files are supported.",
        )

    return content