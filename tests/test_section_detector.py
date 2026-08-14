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
            220,
            100,
        ),
        make_block(
            "2024 - 2025\n"
            "Studio Shodwe\n"
            "Marketing Manager & Specialist",
            220,
            130,
        ),
        make_block(
            "Develop and maintain strong relationships "
            "with partners.",
            220,
            160,
        ),
        make_block(
            "REFERENCE",
            220,
            220,
        ),
        make_block(
            "Harper Richard",
            220,
            250,
        ),
        make_block(
            "Wardiere Inc. / CEO",
            220,
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

from app.services.layout_extractor import TextBlock
from app.services.section_detector import SectionDetector


def make_block(
    text: str,
    x0: float,
    y0: float,
) -> TextBlock:
    return TextBlock(
        page=1,
        page_width=595,
        x0=x0,
        y0=y0,
        x1=x0 + 200,
        y1=y0 + 20,
        text=text,
    )


def test_detect_career_history_as_experience():
    blocks = [
        make_block("Career History", 220, 100),
        make_block("ACME Corp", 220, 130),
    ]

    sections = SectionDetector().detect(blocks)

    assert len(sections) == 1
    assert sections[0].name == "experience"


def test_detect_academic_background_as_education():
    blocks = [
        make_block("Academic Background", 220, 100),
        make_block("Stanford University", 220, 130),
    ]

    sections = SectionDetector().detect(blocks)

    assert len(sections) == 1
    assert sections[0].name == "education"


def test_detect_tech_stack_as_tools():
    blocks = [
        make_block("Tech Stack", 220, 100),
        make_block("Python, Docker, Airflow", 220, 130),
    ]

    sections = SectionDetector().detect(blocks)

    assert len(sections) == 1
    assert sections[0].name == "tools"


def test_detect_core_competencies_as_skills():
    blocks = [
        make_block("Core Competencies", 220, 100),
        make_block("Machine Learning", 220, 130),
    ]

    sections = SectionDetector().detect(blocks)

    assert len(sections) == 1
    assert sections[0].name == "skills"