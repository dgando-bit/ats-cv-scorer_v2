from app.services.education_extractor import EducationExtractor
from app.services.layout_extractor import TextBlock


def test_extract_multiple_educations():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2025-2026 : « Expert en Ingénierie de l’IA » – Niveau 7 (BAC+5)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Mines Paris – PSL Executive Education.",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=160,
            x1=500,
            y1=180,
            text="2018 : « Concepteur-Développeur Informatique » – Niveau 6 (BAC+3/4)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=190,
            x1=500,
            y1=210,
            text="M2I Formation 75.",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=220,
            x1=500,
            y1=240,
            text="2015 : « Développeur Intégrateur Web » – Niveau 6 (BAC+3/4)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=250,
            x1=500,
            y1=270,
            text="Ifocop 75.",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=280,
            x1=500,
            y1=300,
            text="2001: BTS « Informatique Industrielle »",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=310,
            x1=500,
            y1=330,
            text="Lycée ORT Montreuil 93.",
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 4

    assert educations[0].year == "2025-2026"
    assert educations[0].degree == "Expert en Ingénierie de l’IA"
    assert educations[0].institution == "Mines Paris – PSL Executive Education"

    assert educations[1].year == "2018"
    assert educations[1].degree == "Concepteur-Développeur Informatique"
    assert educations[1].institution == "M2I Formation 75"

    assert educations[2].year == "2015"
    assert educations[2].degree == "Développeur Intégrateur Web"
    assert educations[2].institution == "Ifocop 75"

    assert educations[3].year == "2001"
    assert educations[3].degree == "BTS « Informatique Industrielle »"
    assert educations[3].institution == "Lycée ORT Montreuil 93"


def test_extract_education_with_multiline_blocks():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text=(
                "2025-2026 : « Expert en\n"
                "Ingénierie de l’IA » – Niveau 7\n"
                "(BAC+5)\n"
                "Mines Paris – PSL Executive\n"
                "Education."
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text=(
                "2018 : « Concepteur-Développeur\n"
                "Informatique » – Niveau 6\n"
                "(BAC+3/4)\n"
                "M2I Formation 75"
            ),
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 2

    assert educations[0].year == "2025-2026"
    assert educations[0].degree == "Expert en Ingénierie de l’IA"
    assert educations[0].institution == (
        "Mines Paris – PSL Executive Education"
    )

    assert educations[1].year == "2018"
    assert educations[1].degree == (
        "Concepteur-Développeur Informatique"
    )
    assert educations[1].institution == "M2I Formation 75"


def test_extract_education_classic_format():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2019 : Master Data Science",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Université Paris-Saclay",
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].year == "2019"
    assert educations[0].degree == "Master Data Science"
    assert educations[0].institution == "Université Paris-Saclay"


def test_extract_education_year_on_separate_line():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2020",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Master Intelligence Artificielle",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=160,
            x1=500,
            y1=180,
            text="Université Paris Cité",
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].year == "2020"
    assert educations[0].degree == "Master Intelligence Artificielle"
    assert educations[0].institution == "Université Paris Cité"


def test_extract_education_all_on_one_line():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2021 : Master Data Science – Université Paris-Saclay",
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].year == "2021"
    assert educations[0].degree == "Master Data Science"
    assert educations[0].institution == "Université Paris-Saclay"


def test_extract_engineering_degree():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2018 : Diplôme d'ingénieur informatique",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="INSA Lyon",
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].year == "2018"
    assert educations[0].degree == "Diplôme d'ingénieur informatique"
    assert educations[0].institution == "INSA Lyon"


def test_extract_education_multiline_degree():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text=(
                "2022 : « Master\n"
                "Data Science » – Niveau 7\n"
                "Université Paris-Saclay"
            ),
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].year == "2022"
    assert educations[0].degree == "Master Data Science"
    assert educations[0].institution == "Université Paris-Saclay"

def test_extract_education_institution_before_degree():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=33,
            y0=100,
            x1=200,
            y1=120,
            text="2029 - 2030",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=33,
            y0=130,
            x1=250,
            y1=150,
            text="WARDIERE UNIVERSITY",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=41,
            y0=160,
            x1=250,
            y1=180,
            text="Master of Business",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=41,
            y0=190,
            x1=250,
            y1=210,
            text="Management",
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 1

    education = educations[0]

    assert education.year == "2029-2030"
    assert education.institution == "WARDIERE UNIVERSITY"
    assert education.degree == "Master of Business Management"

def test_extract_education_ignores_gpa():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=33,
            y0=100,
            x1=250,
            y1=140,
            text=(
                "2025 - 2029\n"
                "WARDIERE UNIVERSITY"
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=41,
            y0=150,
            x1=250,
            y1=170,
            text="Bachelor of Business",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=41,
            y0=180,
            x1=250,
            y1=200,
            text="GPA: 3.8 / 4.0",
        ),
    ]

    extractor = EducationExtractor()

    educations = extractor.extract(blocks)

    assert len(educations) == 1

    education = educations[0]

    assert education.year == "2025-2029"
    assert education.institution == "WARDIERE UNIVERSITY"
    assert education.degree == "Bachelor of Business"

def test_extract_unknown_university():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2023 - 2025",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Stanford University",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=160,
            x1=500,
            y1=180,
            text="Master of Science in Artificial Intelligence",
        ),
    ]

    extractor = EducationExtractor()
    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].year == "2023-2025"
    assert educations[0].institution == "Stanford University"
    assert educations[0].degree == "Master of Science in Artificial Intelligence"


def test_extract_unknown_school_without_university_keyword():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2021 - 2023",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="General Assembly",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=160,
            x1=500,
            y1=180,
            text="Data Science Program",
        ),
    ]

    extractor = EducationExtractor()
    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].institution == "General Assembly"
    assert educations[0].degree == "Data Science Program"
    assert educations[0].year == "2021-2023"


def test_extract_certification():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2024",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Cloud Academy",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=160,
            x1=500,
            y1=180,
            text="Certification Data Engineer",
        ),
    ]

    extractor = EducationExtractor()
    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].institution == "Cloud Academy"
    assert educations[0].degree == "Certification Data Engineer"
    assert educations[0].year == "2024"


def test_extract_institution_with_numeric_name():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="2020 - 2022",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="42 Paris",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=160,
            x1=500,
            y1=180,
            text="Développement logiciel",
        ),
    ]

    extractor = EducationExtractor()
    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].institution == "42 Paris"
    assert educations[0].degree == "Développement logiciel"
    assert educations[0].year == "2020-2022"

def test_extract_education_with_month_dates():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=100,
            x1=250,
            y1=130,
            text=(
                "Jan 2019 - Feb 2021\n"
                "Bachelor of Business Administration"
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=140,
            x1=250,
            y1=160,
            text="University of Business Excellence",
        ),
    ]

    extractor = EducationExtractor()
    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].year == "Jan 2019-Feb 2021"
    assert educations[0].degree == "Bachelor of Business Administration"
    assert educations[0].institution == "University of Business Excellence"

def test_extract_education_ignores_cgpa():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=100,
            x1=250,
            y1=130,
            text=(
                "Jan 2019 - Feb 2021\n"
                "Bachelor of Business Administration"
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=140,
            x1=250,
            y1=160,
            text="University of Business Excellence",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=35,
            y0=170,
            x1=250,
            y1=190,
            text="Final CGPA: 3.90",
        ),
    ]

    extractor = EducationExtractor()
    educations = extractor.extract(blocks)

    assert len(educations) == 1
    assert educations[0].degree == "Bachelor of Business Administration"
    assert educations[0].institution == "University of Business Excellence"
    assert educations[0].year == "Jan 2019-Feb 2021"