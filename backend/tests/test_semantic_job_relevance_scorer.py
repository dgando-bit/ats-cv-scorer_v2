from app.models.job import JobOffer
from app.services.semantic.semantic_job_relevance_scorer import (
    SemanticJobRelevanceScorer,
)


class FakeSimilarityService:
    def __init__(
        self,
        scores: dict[str, float],
    ) -> None:
        self.scores = scores

    def similarity(
        self,
        query: str,
        document: str,
    ) -> float:
        return self.scores.get(
            document,
            0.0,
        )


def test_semantic_job_relevance_score():
    job = JobOffer(
        title="Software Engineer",
        description=(
            "Conception d'APIs REST "
            "et de services backend."
        ),
        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
    )

    similarity_service = FakeSimilarityService(
        scores={
            "Software Engineer": 0.8,
            "Python FastAPI PostgreSQL": 0.7,
            (
                "Conception d'APIs REST "
                "et de services backend."
            ): 0.9,
        }
    )

    scorer = SemanticJobRelevanceScorer(
        similarity_service=similarity_service,
    )

    result = scorer.score(
        query="développeur backend",
        job=job,
    )

    assert result.title == 0.8
    assert result.skills == 0.7
    assert result.description == 0.9

    assert result.score == 0.79


def test_semantic_job_relevance_empty_query():
    job = JobOffer(
        title="Software Engineer",
        description="Backend development",
        skills=["Python"],
    )

    scorer = SemanticJobRelevanceScorer(
        similarity_service=FakeSimilarityService(
            scores={}
        )
    )

    result = scorer.score(
        query="",
        job=job,
    )

    assert result.title == 0.0
    assert result.skills == 0.0
    assert result.description == 0.0
    assert result.score == 0.0


def test_semantic_job_relevance_handles_missing_signals():
    job = JobOffer(
        title="Software Engineer",
        description="",
        skills=[],
    )

    scorer = SemanticJobRelevanceScorer(
        similarity_service=FakeSimilarityService(
            scores={
                "Software Engineer": 0.8,
            }
        )
    )

    result = scorer.score(
        query="développeur backend",
        job=job,
    )

    assert result.title == 0.8
    assert result.skills == 0.0
    assert result.description == 0.0