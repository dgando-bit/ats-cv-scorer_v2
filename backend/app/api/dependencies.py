from functools import lru_cache

from app.providers.base import JobProvider
from app.providers.france_travail import (
    FranceTravailProvider,
)
from app.services.llm.groq_job_relevance_evaluator import (
    GroqJobRelevanceEvaluator,
)
from app.services.matching.job_search_pipeline import (
    JobSearchPipeline,
)
from app.services.semantic.semantic_similarity_service import (
    SemanticSimilarityService,
)
from app.services.cv.cv_extractor import (
    CVExtractor,
)
from app.services.llm.groq_job_requirements_batch_extractor import (
    GroqJobRequirementsBatchExtractor,
)

@lru_cache
def get_cv_extractor() -> CVExtractor:
    return CVExtractor()

@lru_cache
def get_job_provider() -> JobProvider:
    """
    Réutilise le provider France Travail.

    Cela permet notamment de conserver le token OAuth
    tant qu'il reste valide.
    """
    return FranceTravailProvider()


@lru_cache
def get_semantic_service() -> SemanticSimilarityService:
    """
    Charge le modèle d'embedding une seule fois
    par processus backend.
    """
    return SemanticSimilarityService()


@lru_cache
def get_relevance_evaluator() -> GroqJobRelevanceEvaluator:
    """
    Réutilise le client Groq pour l'évaluation
    de pertinence des offres.
    """
    return GroqJobRelevanceEvaluator()


@lru_cache
def get_job_search_pipeline() -> JobSearchPipeline:
    """
    Singleton du pipeline.

    Important : on réutilise get_job_provider() (et non un
    FranceTravailProvider() flambant neuf) afin de conserver
    entre les requêtes le token OAuth ainsi que le pool de
    connexions HTTP (keep-alive). Cela permet aussi au cache
    mémoire des requirements (self._requirements_cache) du
    pipeline de réellement persister entre deux recherches.
    """
    return JobSearchPipeline(
        provider=get_job_provider(),
        relevance_evaluator=(
            get_relevance_evaluator()
        ),
        semantic_service=(
            get_semantic_service()
        ),
        requirements_batch_extractor=(
            get_requirements_batch_extractor()
        ),
    )

@lru_cache
def get_requirements_batch_extractor(
) -> GroqJobRequirementsBatchExtractor:
    return (
        GroqJobRequirementsBatchExtractor()
    )