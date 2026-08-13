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


def test_extract_experience_multiline_header():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text=(
                "IA & Machine Learning Engineer\n"
                "Liora\n"
                "(2025 - 2026)"
            ),
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
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.role == "IA & Machine Learning Engineer"
    assert experience.company == "Liora"
    assert experience.start_date == "2025"
    assert experience.end_date == "2026"


def test_extract_experience_company_role_date_separate_blocks():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="Airweb - Paragon ID",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=125,
            x1=500,
            y1=145,
            text="Développeur Back-end",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=150,
            x1=500,
            y1=170,
            text="(2021 - 2025)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=180,
            x1=500,
            y1=200,
            text="Conception d'APIs REST.",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.company == "Airweb - Paragon ID"
    assert experience.role == "Développeur Back-end"
    assert experience.start_date == "2021"
    assert experience.end_date == "2025"


def test_extract_experience_present_date():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="Data Engineer - ACME (2024 - présent)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text="Construction de pipelines de données.",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.start_date == "2024"
    assert experience.end_date == "présent"


def test_extract_experience_description_multiline_block():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=100,
            x1=500,
            y1=120,
            text="Data Engineer ACME (2024 - 2025)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=200,
            y0=130,
            x1=500,
            y1=150,
            text=(
                "Conception de pipelines de données pour alimenter les APIs.\n"
                "Transformation et nettoyage des données.\n"
                "Industrialisation des traitements."
            ),
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.description == [
        "Conception de pipelines de données pour alimenter les APIs.",
        "Transformation et nettoyage des données.",
        "Industrialisation des traitements.",
    ]

def test_extract_generic_multiline_role_company():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text=(
                "2030 - PRESENT\n"
                "Borcelle Studio\n"
                "Marketing Manager & Specialist"
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=240,
            y0=150,
            x1=550,
            y1=180,
            text="Develop comprehensive marketing strategies.",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.company == "Borcelle Studio"
    assert experience.role == "Marketing Manager & Specialist"
    assert experience.start_date == "2030"
    assert experience.end_date == "PRESENT"


def test_extract_generic_french_role_company():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text=(
                "2022 - 2025\n"
                "ACME France\n"
                "Chef de projet Data"
            ),
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.company == "ACME France"
    assert experience.role == "Chef de projet Data"

def test_merge_wrapped_description_lines():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=130,
            text=(
                "2030 - PRESENT\n"
                "Borcelle Studio\n"
                "Marketing Manager & Specialist"
            ),
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=240,
            y0=150,
            x1=550,
            y1=190,
            text=(
                "Develop and execute comprehensive marketing strategies and\n"
                "campaigns that align with the company's goals and objectives."
            ),
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert experiences[0].description == [
        (
            "Develop and execute comprehensive marketing strategies and "
            "campaigns that align with the company's goals and objectives."
        )
    ]


def test_merge_fragmented_description_words():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=130,
            text="Développeur Back-end Airweb (2021 - 2025)",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=240,
            y0=150,
            x1=550,
            y1=220,
            text=(
                "Concevoir,\n"
                "implémenter\n"
                "et\n"
                "optimiser\n"
                "les\n"
                "bases\n"
                "de\n"
                "données\n"
                "(modélisations requêtes, intégrité)"
            ),
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert experiences[0].description == [
        (
            "Concevoir, implémenter et optimiser les bases de données "
            "(modélisations requêtes, intégrité)"
        )
    ]

def test_extract_generic_cloud_architect():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text=(
                "2022 - 2025\n"
                "ACME Cloud\n"
                "Cloud Architect"
            ),
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1
    assert experiences[0].company == "ACME Cloud"
    assert experiences[0].role == "Cloud Architect"


def test_extract_generic_product_owner():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text=(
                "2021 - 2024\n"
                "FinTech Corp\n"
                "Product Owner"
            ),
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1
    assert experiences[0].company == "FinTech Corp"
    assert experiences[0].role == "Product Owner"


def test_extract_generic_bi_analyst():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text=(
                "2020 - 2023\n"
                "DataVision\n"
                "Analyste BI"
            ),
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1
    assert experiences[0].company == "DataVision"
    assert experiences[0].role == "Analyste BI"


def test_extract_generic_data_platform_lead():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text=(
                "2023 - PRESENT\n"
                "Example Tech\n"
                "Data Platform Lead"
            ),
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1
    assert experiences[0].company == "Example Tech"
    assert experiences[0].role == "Data Platform Lead"

def test_extract_generic_single_line_role_before_company():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text="Cloud Architect ACME Cloud (2022 - 2025)",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1
    assert experiences[0].company == "ACME Cloud"
    assert experiences[0].role == "Cloud Architect"


def test_extract_generic_single_line_company_before_role():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text="ACME Cloud (2022 - 2025) Cloud Architect",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1
    assert experiences[0].company == "ACME Cloud"
    assert experiences[0].role == "Cloud Architect"


def test_extract_generic_single_line_product_owner():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text="Product Owner FinTech Corp (2021 - 2024)",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1
    assert experiences[0].company == "FinTech Corp"
    assert experiences[0].role == "Product Owner"


def test_extract_generic_single_line_bi_analyst():
    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=220,
            y0=100,
            x1=550,
            y1=140,
            text="DataVision (2020 - 2023) Analyste BI",
        ),
    ]

    extractor = ExperienceExtractor()

    experiences = extractor.extract(blocks)

    assert len(experiences) == 1
    assert experiences[0].company == "DataVision"
    assert experiences[0].role == "Analyste BI"