from app.services.layout_extractor import TextBlock
from app.services.section_detector import SectionDetector


def make_block(
    text: str,
    y: float,
    x: float = 220,
) -> TextBlock:
    return TextBlock(
        page=1,
        page_width=595,
        x0=x,
        y0=y,
        x1=550,
        y1=y + 15,
        text=text,
    )


def test_reference_section_stops_experience_section():
    blocks = [
        make_block(
            "WORK EXPERIENCE",
            100,
        ),
        make_block(
            "2024 - 2025\n"
            "Studio Shodwe\n"
            "Marketing Manager & Specialist",
            130,
        ),
        make_block(
            "Develop and maintain strong relationships "
            "with partners.",
            160,
        ),
        make_block(
            "REFERENCE",
            220,
        ),
        make_block(
            "Harper Richard",
            250,
        ),
        make_block(
            "Wardiere Inc. / CEO",
            270,
        ),
    ]

    detector = SectionDetector()

    sections = detector.detect(blocks)

    sections_by_name = {
        section.name: section
        for section in sections
    }

    assert "experience" in sections_by_name
    assert "references" in sections_by_name

    experience_texts = [
        block.text
        for block in sections_by_name["experience"].blocks
    ]

    reference_texts = [
        block.text
        for block in sections_by_name["references"].blocks
    ]

    assert len(experience_texts) == 2

    assert "Harper Richard" not in experience_texts
    assert "Wardiere Inc. / CEO" not in experience_texts

    assert "Harper Richard" in reference_texts
    assert "Wardiere Inc. / CEO" in reference_texts