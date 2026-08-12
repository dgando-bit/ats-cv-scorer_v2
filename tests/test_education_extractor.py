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