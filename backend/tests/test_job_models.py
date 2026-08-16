# tests/test_job_models.py

from app.models.job import JobOffer


def test_create_job_offer():
    job = JobOffer(
        id="12345",
        title="Machine Learning Engineer",
        company="ACME",
        location="Paris",
        contract_type="CDI",
        description="Nous recherchons un ML Engineer.",
        skills=[
            "Python",
            "Machine Learning",
        ],
        tools=[
            "Docker",
            "MLflow",
        ],
        source="france_travail",
    )

    assert job.title == "Machine Learning Engineer"
    assert job.company == "ACME"
    assert "Python" in job.skills
    assert job.source == "france_travail"


def test_job_offer_optional_fields():
    job = JobOffer(
        title="Data Engineer",
        description="Construction de pipelines data.",
    )

    assert job.company is None
    assert job.skills == []
    assert job.tools == []