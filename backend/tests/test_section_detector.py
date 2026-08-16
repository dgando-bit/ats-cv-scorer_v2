from app.services.cv.layout_extractor import TextBlock
from app.services.cv.section_detector import SectionDetector


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

def test_detect_multiple_section_headings_in_same_block():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=100,
            x1=480,
            y1=120,
            text="KEY SKILLS\nLANGUAGE",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=50,
            y0=130,
            x1=150,
            y1=150,
            text="Client Acquisition",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=420,
            y0=130,
            x1=520,
            y1=150,
            text="English (Fluent)",
        ),
    ]

    sections = SectionDetector().detect(blocks)

    names = [
        section.name
        for section in sections
    ]

    assert "skills" in names
    assert "languages" in names

def test_assign_blocks_under_multiple_headings_by_position():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=100,
            x1=480,
            y1=120,
            text="KEY SKILLS\nLANGUAGE",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=50,
            y0=130,
            x1=150,
            y1=150,
            text="Client Acquisition",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=230,
            y0=130,
            x1=330,
            y1=150,
            text="Problem-Solving",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=420,
            y0=130,
            x1=520,
            y1=150,
            text="English (Fluent)",
        ),
    ]

    sections = SectionDetector().detect(blocks)

    sections_by_name = {
        section.name: section
        for section in sections
    }

    assert "skills" in sections_by_name
    assert "languages" in sections_by_name

    skills_texts = [
        block.text
        for block in sections_by_name["skills"].blocks
    ]

    languages_texts = [
        block.text
        for block in sections_by_name["languages"].blocks
    ]

    assert "Client Acquisition" in skills_texts
    assert "Problem-Solving" in skills_texts
    assert "English (Fluent)" in languages_texts

def test_parallel_sections_are_detected_before_global_column_split():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=100,
            x1=480,
            y1=120,
            text="KEY SKILLS\nLANGUAGE",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=53,
            y0=130,
            x1=150,
            y1=150,
            text="Client Acquisition",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=233,
            y0=130,
            x1=330,
            y1=150,
            text="Problem-Solving",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=414,
            y0=130,
            x1=520,
            y1=150,
            text="English (Fluent)",
        ),
    ]

    detector = SectionDetector()

    sections = detector.detect(blocks)

    sections_by_name = {
        section.name: section
        for section in sections
    }

    skills_texts = [
        block.text
        for block in sections_by_name["skills"].blocks
    ]

    languages_texts = [
        block.text
        for block in sections_by_name["languages"].blocks
    ]

    assert skills_texts == [
        "Client Acquisition",
        "Problem-Solving",
    ]

    assert languages_texts == [
        "English (Fluent)",
    ]

def test_realistic_mixed_layout_with_parallel_bottom_sections():
    blocks = [
        # SUMMARY à droite
        TextBlock(
            page=1,
            page_width=595,
            x0=232,
            y0=165,
            x1=307,
            y1=185,
            text="SUMMARY",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=232,
            y0=190,
            x1=573,
            y1=243,
            text="Administrative professional profile.",
        ),

        # EDUCATION à gauche
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=594,
            x1=122,
            y1=614,
            text="EDUCATION",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=620,
            x1=228,
            y1=650,
            text="Jan 2019 - Feb 2021\nBachelor of Business Administration",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=651,
            x1=204,
            y1=666,
            text="University of Business Excellence",
        ),

        # Deuxième formation à droite
        TextBlock(
            page=1,
            page_width=595,
            x0=306,
            y0=620,
            x1=511,
            y1=650,
            text="Jan 2018 - Dec 2018\nFoundation in Business Administration",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=306,
            y0=651,
            x1=401,
            y1=666,
            text="Borcelle University",
        ),

        # Multi-heading bas de page
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=734,
            x1=477,
            y1=754,
            text="KEY SKILLS\nLANGUAGE",
        ),

        # Skills colonne 1
        TextBlock(
            page=1,
            page_width=595,
            x0=53,
            y0=760,
            x1=143,
            y1=774,
            text="Client Acquisition",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=53,
            y0=779,
            x1=102,
            y1=793,
            text="B2B Sales",
        ),

        # Skills colonne 2
        TextBlock(
            page=1,
            page_width=595,
            x0=234,
            y0=760,
            x1=320,
            y1=774,
            text="Negotiation Skills",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=234,
            y0=779,
            x1=318,
            y1=793,
            text="Problem-Solving",
        ),

        # Languages
        TextBlock(
            page=1,
            page_width=595,
            x0=414,
            y0=760,
            x1=492,
            y1=774,
            text="English (Fluent)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=414,
            y0=779,
            x1=486,
            y1=793,
            text="Malay (Fluent)",
        ),
    ]

    sections = SectionDetector().detect(blocks)

    sections_by_name = {
        section.name: section
        for section in sections
    }

    skills_texts = [
        block.text
        for block in sections_by_name["skills"].blocks
    ]

    language_texts = [
        block.text
        for block in sections_by_name["languages"].blocks
    ]

    assert "Client Acquisition" in skills_texts
    assert "B2B Sales" in skills_texts
    assert "Negotiation Skills" in skills_texts
    assert "Problem-Solving" in skills_texts

    assert "English (Fluent)" in language_texts
    assert "Malay (Fluent)" in language_texts

def test_education_section_can_span_two_columns():
    blocks = [
        # Profile à droite, plus haut
        TextBlock(
            page=1,
            page_width=595,
            x0=232,
            y0=165,
            x1=307,
            y1=185,
            text="SUMMARY",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=232,
            y0=190,
            x1=573,
            y1=243,
            text="Administrative professional profile.",
        ),

        # Heading education à gauche
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=594,
            x1=122,
            y1=614,
            text="EDUCATION",
        ),

        # Formation 1 à gauche
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=620,
            x1=228,
            y1=650,
            text=(
                "Jan 2019 - Feb 2021\n"
                "Bachelor of Business Administration"
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=651,
            x1=204,
            y1=666,
            text="University of Business Excellence",
        ),

        # Formation 2 à droite
        TextBlock(
            page=1,
            page_width=595,
            x0=306,
            y0=620,
            x1=511,
            y1=650,
            text=(
                "Jan 2018 - Dec 2018\n"
                "Foundation in Business Administration"
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=306,
            y0=651,
            x1=401,
            y1=666,
            text="Borcelle University",
        ),
    ]

    sections = SectionDetector().detect(blocks)

    education_blocks = [
        block
        for section in sections
        if section.name == "education"
        for block in section.blocks
    ]

    education_texts = [
        block.text
        for block in education_blocks
    ]

    assert any(
        "Bachelor of Business Administration" in text
        for text in education_texts
    )

    assert any(
        "Foundation in Business Administration" in text
        for text in education_texts
    )

    assert "Borcelle University" in education_texts

def test_spanning_education_preserves_column_order():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=594,
            x1=122,
            y1=614,
            text="EDUCATION",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=620,
            x1=228,
            y1=650,
            text="Jan 2019 - Feb 2021\nBachelor of Business Administration",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=651,
            x1=204,
            y1=666,
            text="University of Business Excellence",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=306,
            y0=620,
            x1=511,
            y1=650,
            text="Jan 2018 - Dec 2018\nFoundation in Business Administration",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=306,
            y0=651,
            x1=401,
            y1=666,
            text="Borcelle University",
        ),
    ]

    sections = SectionDetector().detect(blocks)

    education = next(
        section
        for section in sections
        if section.name == "education"
    )

    texts = [block.text for block in education.blocks]

    assert texts == [
        "Jan 2019 - Feb 2021\nBachelor of Business Administration",
        "University of Business Excellence",
        "Jan 2018 - Dec 2018\nFoundation in Business Administration",
        "Borcelle University",
    ]

def test_parallel_sidebar_section_does_not_capture_main_experience():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=33,
            y0=350,
            x1=120,
            y1=370,
            text="EDUCATION",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=244,
            y0=350,
            x1=350,
            y1=370,
            text="EXPERIENCE",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=33,
            y0=382,
            x1=180,
            y1=400,
            text="2029 - 2030",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=244,
            y0=364,
            x1=500,
            y1=395,
            text=(
                "2030 - PRESENT\n"
                "Borcelle Studio\n"
                "Marketing Manager & Specialist"
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=244,
            y0=485,
            x1=500,
            y1=515,
            text=(
                "2025 - 2029\n"
                "Fauget Studio\n"
                "Marketing Manager & Specialist"
            ),
        ),
    ]

    sections = SectionDetector().detect(blocks)

    experience_blocks = [
        block
        for section in sections
        if section.name == "experience"
        for block in section.blocks
    ]

    texts = [block.text for block in experience_blocks]

    assert any(
        "Borcelle Studio" in text
        for text in texts
    )

    assert any(
        "Fauget Studio" in text
        for text in texts
    )