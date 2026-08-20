import numpy as np

from app.services.semantic.semantic_similarity_service import (
    SemanticSimilarityService,
)


class FakeModel:
    def encode(
        self,
        sentences,
        normalize_embeddings=True,
    ):
        return np.array(
            [
                [1.0, 0.0],
                [0.8, 0.6],
            ]
        )


def test_semantic_similarity():
    service = SemanticSimilarityService.__new__(
        SemanticSimilarityService
    )

    service.model = FakeModel()

    score = service.similarity(
        query="machine learning",
        document="data scientist",
    )

    assert score == 0.8


def test_semantic_similarity_returns_zero_for_empty_text():
    service = SemanticSimilarityService.__new__(
        SemanticSimilarityService
    )

    service.model = FakeModel()

    assert service.similarity("", "test") == 0.0
    assert service.similarity("test", "") == 0.0