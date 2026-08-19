from app.models.job import JobOffer
from app.services.matching.job_relevance_scorer import (
    JobRelevanceScorer,
)


def test_high_relevance_when_query_is_in_title():
    job = JobOffer(
        title="Machine Learning Engineer",
        description=(
            "Développement et déploiement "
            "de modèles de machine learning."
        ),
    )

    score = JobRelevanceScorer().score(
        job,
        "machine learning",
    )

    assert score == 100.0


def test_lower_relevance_when_query_only_in_description():
    job = JobOffer(
        title="Ingénieur sécurité informatique",
        description=(
            "Travail sur la cybersécurité, "
            "avec ponctuellement des techniques "
            "de machine learning."
        ),
    )

    score = JobRelevanceScorer().score(
        job,
        "machine learning",
    )

    assert score == 30.0


def test_partial_relevance():
    job = JobOffer(
        title="Machine Vision Engineer",
        description="Computer vision et Python.",
    )

    score = JobRelevanceScorer().score(
        job,
        "machine learning",
    )

    assert score == 35.0


def test_irrelevant_job():
    job = JobOffer(
        title="Comptable",
        description=(
            "Gestion comptable et facturation."
        ),
    )

    score = JobRelevanceScorer().score(
        job,
        "machine learning",
    )

    assert score == 0.0


def test_empty_keywords():
    job = JobOffer(
        title="Data Scientist",
        description="Machine learning",
    )

    score = JobRelevanceScorer().score(
        job,
        "",
    )

    assert score == 0.0