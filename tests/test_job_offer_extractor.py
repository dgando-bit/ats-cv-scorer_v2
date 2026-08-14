from app.services.job_offer_extractor import (
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