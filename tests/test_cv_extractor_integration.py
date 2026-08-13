from pathlib import Path

from app.services.cv_extractor import CVExtractor


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