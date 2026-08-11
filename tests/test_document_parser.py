from pathlib import Path

import pytest

from app.services.document_parser import DocumentParser


def test_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file format"):
        DocumentParser.parse("resume.txt")


def test_pdf_parser():
    sample = Path("data/samples/cv_test.pdf")

    if not sample.exists():
        pytest.skip("Sample PDF not available")

    text = DocumentParser.parse_pdf(sample)

    assert isinstance(text, str)
    assert len(text) > 0


def test_docx_parser():
    sample = Path("data/samples/cv_test.docx")

    if not sample.exists():
        pytest.skip("Sample DOCX not available")

    text = DocumentParser.parse_docx(sample)

    assert isinstance(text, str)
    assert len(text) > 0