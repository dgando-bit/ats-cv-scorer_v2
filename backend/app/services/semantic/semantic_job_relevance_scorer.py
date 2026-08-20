from dataclasses import dataclass

from app.models.job import JobOffer
from app.services.semantic.semantic_similarity_service import (
    SemanticSimilarityService,
)


@dataclass(frozen=True)
class SemanticRelevanceDetails:
    title: float
    skills: float
    description: float
    score: float


class SemanticJobRelevanceScorer:
    TITLE_WEIGHT = 0.50
    SKILLS_WEIGHT = 0.30
    DESCRIPTION_WEIGHT = 0.20

    def __init__(
        self,
        similarity_service: SemanticSimilarityService | None = None,
    ) -> None:
        self.similarity_service = (
            similarity_service
            or SemanticSimilarityService()
        )

    def score(
        self,
        query: str,
        job: JobOffer,
    ) -> SemanticRelevanceDetails:
        if not query.strip():
            return SemanticRelevanceDetails(
                title=0.0,
                skills=0.0,
                description=0.0,
                score=0.0,
            )

        title_score = self._similarity(
            query=query,
            text=job.title,
        )

        skills_text = " ".join(
            job.skills
        )

        skills_score = self._similarity(
            query=query,
            text=skills_text,
        )

        description_score = self._similarity(
            query=query,
            text=job.description,
        )

        weighted_score = (
            title_score * self.TITLE_WEIGHT
            + skills_score * self.SKILLS_WEIGHT
            + description_score
            * self.DESCRIPTION_WEIGHT
        )

        return SemanticRelevanceDetails(
            title=round(title_score, 4),
            skills=round(skills_score, 4),
            description=round(
                description_score,
                4,
            ),
            score=round(weighted_score, 4),
        )

    def _similarity(
        self,
        query: str,
        text: str | None,
    ) -> float:
        if not text or not text.strip():
            return 0.0

        return self.similarity_service.similarity(
            query=query,
            document=text,
        )