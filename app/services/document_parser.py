from pathlib import Path

import fitz
from docx import Document


class DocumentParser:
    """Extract raw text from supported document formats."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

    @staticmethod
    def parse_pdf(file_path: str | Path) -> str:
        """Extract text from a PDF file."""

        document = fitz.open(file_path)

        pages = []

        try:
            for page in document:
                text = page.get_text("text")

                if text.strip():
                    pages.append(text.strip())

        finally:
            document.close()

        return "\n\n".join(pages)

    @staticmethod
    def parse_docx(file_path: str | Path) -> str:
        """Extract text from a DOCX file."""

        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        return "\n".join(paragraphs)

    @classmethod
    def parse(cls, file_path: str | Path) -> str:
        """Extract text based on the file extension."""

        path = Path(file_path)

        extension = path.suffix.lower()

        if extension == ".pdf":
            return cls.parse_pdf(path)

        if extension == ".docx":
            return cls.parse_docx(path)

        supported = ", ".join(sorted(cls.SUPPORTED_EXTENSIONS))

        raise ValueError(
            f"Unsupported file format: {extension}. "
            f"Supported formats: {supported}"
        )