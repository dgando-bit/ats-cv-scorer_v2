import pytest
from app.services.jobs.job_offer_extractor import (
    JobOfferExtractor,
)


def test_extract_job_offer_requirements():

    text = """
    Nous recherchons un Machine Learning Engineer
    avec 3 ans d'expérience.

    Maîtrise de Python, SQL et Scikit-learn requise.

    Docker et MLflow sont appréciés.

    Formation Bac+5 en informatique ou data science.

    Anglais professionnel.
    """

    extractor = JobOfferExtractor()

    job = extractor.extract(
        text,
        title="Machine Learning Engineer",
        company="ACME",
        location="Paris",
    )

    assert job.title == "Machine Learning Engineer"

    assert "python" in job.skills
    assert "sql" in job.skills

    assert "scikit-learn" in job.tools
    assert "docker" in job.tools
    assert "mlflow" in job.tools

    assert job.experience_required == "3 ans"

    assert (
        job.education_required.lower()
        == "bac+5"
    )

    assert "Anglais" in job.languages


def test_extract_job_offer_without_requirements():

    extractor = JobOfferExtractor()

    job = extractor.extract(
        "Une entreprise recherche un développeur.",
        title="Développeur",
    )

    assert job.skills == []
    assert job.tools == []
    assert job.languages == []
    assert job.experience_required is None
    assert job.education_required is None



@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Minimum 5 ans d'expérience en IA / ML / MLOps.",
            "5 ans",
        ),
        (
            "2+ ans d'expérience en IA / ML.",
            "2+ ans",
        ),
        (
            "Au moins 3 ans d'expérience en Data Science.",
            "3 ans",
        ),
        (
            "Vous justifiez de 4 années d'expérience.",
            "4 ans",
        ),
        (
            "Une expérience de 3 ans en Machine Learning est requise.",
            "3 ans",
        ),
        (
            "Expérience professionnelle : 5 ans.",
            "5 ans",
        ),
    ],
)
def test_extract_experience_requirement(
    text,
    expected,
):
    extractor = JobOfferExtractor()

    job = extractor.extract(
        text=text,
        title="AI Engineer",
    )

    assert job.experience_required == expected

def test_no_experience_requirement():

    extractor = JobOfferExtractor()

    job = extractor.extract(
        text=(
            "Nous recherchons un Machine Learning Engineer. "
            "Python et Docker sont utilisés."
        ),
        title="Machine Learning Engineer",
    )

    assert job.experience_required is None