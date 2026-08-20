import numpy as np

from app.services.semantic.job_reranker import (
    JobReranker,
)


class FakeCrossEncoder:
    def predict(self, pairs):
        return np.array(
            [
                0.2,
                0.9,
                0.5,
            ][:len(pairs)]
        )


def make_service() -> JobReranker:
    service = JobReranker.__new__(
        JobReranker
    )
    service.model = FakeCrossEncoder()

    return service


def test_reranker_score():
    service = make_service()

    score = service.score(
        query="développeur backend",
        document=(
            "Software Engineer spécialisé "
            "dans les APIs REST."
        ),
    )

    assert score == 0.2


def test_reranker_ranks_documents():
    service = make_service()

    documents = [
        "Frontend Engineer React",
        "Software Engineer APIs REST",
        "DevOps Engineer Kubernetes",
    ]

    ranking = service.rank(
        query="développeur backend",
        documents=documents,
    )

    assert ranking == [
        (1, 0.9),
        (2, 0.5),
        (0, 0.2),
    ]


def test_reranker_returns_empty_for_empty_query():
    service = make_service()

    assert service.rank(
        query="",
        documents=["test"],
    ) == []


def test_reranker_returns_empty_for_empty_documents():
    service = make_service()

    assert service.rank(
        query="test",
        documents=[],
    ) == []