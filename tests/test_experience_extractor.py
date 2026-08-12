from app.services.experience_extractor import ExperienceExtractor
from app.services.layout_extractor import TextBlock


def test_extract_experience_role_before_company():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="IA & Machine Learning Engineer Liora (2025 - 2026)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Projet académique : Analyse de données, Computer Vision & MLOps",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.role == "IA & Machine Learning Engineer"
    assert experience.company == "Liora"
    assert experience.start_date == "2025"
    assert experience.end_date == "2026"


def test_extract_experience_company_before_role():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="Adiict | Findeur | Cotep (2015 - 2021) Développeur Informatique",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Domaine : Affichage dynamique temps réel & Web-to-Print / SaaS",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.company == "Adiict | Findeur | Cotep"
    assert experience.role == "Développeur Informatique"
    assert experience.start_date == "2015"
    assert experience.end_date == "2021"

def test_extract_comelli_experience():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="Comelli | TI-Median (2008 - 2014) Responsable Informatique",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Domaine : imprimerie",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=160,
            x1=500,
            y1=180,
            text="Gérer le parc informatique et mettre en place les procédures.",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.company == "Comelli | TI-Median"
    assert experience.role == "Responsable Informatique"
    assert experience.start_date == "2008"
    assert experience.end_date == "2014"

    assert len(experience.description) == 2
    assert "imprimerie" in experience.description[0]

def test_extract_multiple_experiences():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="IA & Machine Learning Engineer Liora (2025 - 2026)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Analyse de données, Computer Vision & MLOps",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=200,
            x1=500,
            y1=220,
            text="Développeur Back-end Airweb - Paragon ID (2021 - 2025)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=230,
            x1=500,
            y1=250,
            text="Conception d'APIs REST à forte disponibilité.",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 2

    assert experiences[0].company == "Liora"
    assert experiences[0].role == "IA & Machine Learning Engineer"

    assert experiences[1].company == "Airweb - Paragon ID"
    assert experiences[1].role == "Développeur Back-end"