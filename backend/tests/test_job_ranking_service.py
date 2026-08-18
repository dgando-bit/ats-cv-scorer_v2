from app.models.cv import CV
from app.models.job import JobOffer
from app.services.matching.job_ranking_service import (
    JobRankingService,
)


def test_rank_jobs_by_matching_score():

    cv = CV(
        candidate_name="John Doe",
        title="Machine Learning Engineer",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        tools=[
            "Docker",
            "MLflow",
        ],
        languages=[
            "English",
        ],
        experiences=[],
        education=[],
    )

    jobs = [
        JobOffer(
            id="LOW",
            title="Java Developer",
            description=(
                "Java, Spring Boot, Maven."
            ),
        ),
        JobOffer(
            id="HIGH",
            title="Machine Learning Engineer",
            description=(
                "Compétences requises : "
                "Python, SQL, Machine Learning. "
                "Docker et MLflow."
            ),
        ),
    ]

    service = JobRankingService()

    result = service.rank(
        cv=cv,
        jobs=jobs,
    )

    assert result.candidate_name == "John Doe"
    assert len(result.jobs) == 2

    assert result.jobs[0].match.score >= (
        result.jobs[1].match.score
    )

    assert result.jobs[0].job.id == "HIGH"