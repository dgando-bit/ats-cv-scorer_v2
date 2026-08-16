from pathlib import Path

from app.services.cv.cv_extractor import CVExtractor


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CV_TEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "samples"
    / "cv_test.pdf"
)


def test_extract_real_cv():
    extractor = CVExtractor()

    cv = extractor.extract(
        str(CV_TEST_PATH)
    )

    # ---------------------------------------------------------
    # Identité
    # ---------------------------------------------------------

    assert cv.candidate_name == "Destin GANDO"

    assert cv.title == (
        "MACHINE LEARNING ENGINEER"
    )

    # ---------------------------------------------------------
    # Contact
    # ---------------------------------------------------------

    assert cv.contact.email == (
        "d.gbakary@outlook.com"
    )

    assert cv.contact.phone == (
        "+33 6 70 50 41 98"
    )

    assert cv.contact.location == (
        "Thiais, France"
    )

    # ---------------------------------------------------------
    # Expériences
    # ---------------------------------------------------------

    assert len(cv.experiences) == 4

    # Liora
    experience = cv.experiences[0]

    assert experience.company == "Liora"

    assert experience.role == (
        "IA & Machine Learning Engineer"
    )

    assert experience.start_date == "2025"
    assert experience.end_date == "2026"

    # Airweb
    experience = cv.experiences[1]

    assert experience.company == (
        "Airweb - Paragon ID"
    )

    assert experience.role == (
        "Développeur Back-end"
    )

    assert experience.start_date == "2021"
    assert experience.end_date == "2025"

    # Adiict
    experience = cv.experiences[2]

    assert experience.company == (
        "Adiict | Findeur | Cotep"
    )

    assert experience.role == (
        "Développeur Informatique"
    )

    assert experience.start_date == "2015"
    assert experience.end_date == "2021"

    # Comelli
    experience = cv.experiences[3]

    assert experience.company == (
        "Comelli | TI-Median"
    )

    assert experience.role == (
        "Responsable Informatique"
    )

    assert experience.start_date == "2008"
    assert experience.end_date == "2014"

    # ---------------------------------------------------------
    # Formation
    # ---------------------------------------------------------

    assert len(cv.education) == 4

    education = cv.education[0]

    assert education.year == "2025-2026"

    assert education.degree == (
        "Expert en Ingénierie de l’IA"
    )

    assert education.institution == (
        "Mines Paris – PSL Executive Education"
    )

    education = cv.education[3]

    assert education.year == "2001"

    assert education.degree == (
        "BTS « Informatique Industrielle »"
    )

    assert education.institution == (
        "Lycée ORT Montreuil 93"
    )

    # ---------------------------------------------------------
    # Compétences
    # ---------------------------------------------------------

    assert "Modélisation ML (Scikit-learn)" in (
        cv.skills
    )

    assert "Deep Learning" in cv.skills
    assert "LLM" in cv.skills
    assert "RAG" in cv.skills

    # ---------------------------------------------------------
    # Langues
    # ---------------------------------------------------------

    assert "Anglais (B2)" in cv.languages
    assert "LSF (C2)" in cv.languages

def test_extract_second_real_cv():
    extractor = CVExtractor()

    cv = extractor.extract(
        str(
            PROJECT_ROOT
            / "data"
            / "samples"
            / "cv_test_1.pdf"
        )
    )

    assert cv.candidate_name == "RICHARD SANCHEZ"
    assert cv.title == "MARKETING MANAGER"

    assert len(cv.experiences) == 3

    assert cv.experiences[0].company == "Borcelle Studio"
    assert cv.experiences[0].role == "Marketing Manager & Specialist"
    assert cv.experiences[0].start_date == "2030"
    assert cv.experiences[0].end_date == "PRESENT"

    assert cv.experiences[1].company == "Fauget Studio"
    assert cv.experiences[2].company == "Studio Shodwe"

    assert len(cv.education) == 2

    assert cv.education[0].institution == "WARDIERE UNIVERSITY"
    assert cv.education[0].degree == "Master of Business Management"
    assert cv.education[0].year == "2029-2030"

    assert cv.education[1].institution == "WARDIERE UNIVERSITY"
    assert cv.education[1].degree == "Bachelor of Business"
    assert cv.education[1].year == "2025-2029"

    assert "Project Management" in cv.skills
    assert "English (Fluent)" in cv.languages