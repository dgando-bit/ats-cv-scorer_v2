from functools import lru_cache
from app.providers.base import JobProvider
from app.providers.france_travail import FranceTravailProvider

from app.providers.france_travail import FranceTravailProvider
from app.services.llm.groq_job_relevance_evaluator import (
    GroqJobRelevanceEvaluator,
)
from app.services.matching.job_search_pipeline import (
    JobSearchPipeline,
)
from app.services.semantic.semantic_similarity_service import (
    SemanticSimilarityService,
)


def get_job_provider() -> JobProvider:
    return FranceTravailProvider()

@lru_cache
def get_semantic_service() -> SemanticSimilarityService:
    return SemanticSimilarityService()


@lru_cache
def get_relevance_evaluator() -> GroqJobRelevanceEvaluator:
    return GroqJobRelevanceEvaluator()


def get_job_search_pipeline() -> JobSearchPipeline:
    return JobSearchPipeline(
        provider=FranceTravailProvider(),
        relevance_evaluator=get_relevance_evaluator(),
        semantic_service=get_semantic_service(),
    )