import time
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from dataclasses import dataclass
from threading import Lock

from groq import RateLimitError

from app.models.cv import CV
from app.models.job import JobOffer
from app.models.ranking import (
    JobRankingResult,
    RankedJob,
)
from app.providers.base import JobProvider
from app.services.jobs.job_offer_extractor import (
    JobOfferExtractor,
)
from app.services.jobs.job_requirements_mapper import (
    JobRequirementsMapper,
)
from app.services.llm.base import (
    JobRelevanceEvaluator,
)
from app.services.llm.groq_job_requirements_extractor import (
    GroqJobRequirementsExtractor,
)
from app.services.matching.match_explanation_service import (
    MatchExplanationService,
)
from app.services.matching.matching_engine import (
    MatchingEngine,
)
from app.services.semantic.semantic_similarity_service import (
    SemanticSimilarityService,
)


@dataclass(frozen=True)
class CandidateJob:
    job: JobOffer
    semantic_score: float


class JobSearchPipeline:
    MAX_GROQ_WORKERS = 2
    MAX_GROQ_ATTEMPTS = 3

    def __init__(
        self,
        provider: JobProvider,
        relevance_evaluator: JobRelevanceEvaluator,
        semantic_service: SemanticSimilarityService | None = None,
        job_offer_extractor: JobOfferExtractor | None = None,
        requirements_extractor: GroqJobRequirementsExtractor | None = None,
        matching_engine: MatchingEngine | None = None,
        explanation_service: MatchExplanationService | None = None,
    ) -> None:
        self.provider = provider
        self.relevance_evaluator = (
            relevance_evaluator
        )

        self.semantic_service = (
            semantic_service
            or SemanticSimilarityService()
        )

        self.job_offer_extractor = (
            job_offer_extractor
            or JobOfferExtractor()
        )

        self.requirements_extractor = (
            requirements_extractor
            or GroqJobRequirementsExtractor()
        )

        self.matching_engine = (
            matching_engine
            or MatchingEngine()
        )

        self.explanation_service = (
            explanation_service
            or MatchExplanationService()
        )

        # ---------------------------------------------------------
        # Cache mémoire des offres déjà enrichies par Groq
        # ---------------------------------------------------------

        self._requirements_cache: dict[
            str,
            JobOffer,
        ] = {}

        # Le pipeline peut appeler l'extracteur depuis plusieurs
        # threads. Le lock protège le dictionnaire partagé.
        self._requirements_cache_lock = Lock()

    def search_and_rank(
            self,
            cv: CV,
            keywords: str,
            location: str | None = None,
            insee_code: str | None = None,
            provider_limit: int = 50,
            retrieval_top_k: int = 20,
            final_limit: int = 5,
    ) -> JobRankingResult:

        # ---------------------------------------------------------
        # 1. Limites de recherche
        # ---------------------------------------------------------

        final_limit = max(
            1,
            final_limit,
        )

        provider_limit = max(
            provider_limit,
            final_limit * 2,
        )

        retrieval_top_k = max(
            retrieval_top_k,
            final_limit,
        )

        retrieval_top_k = min(
            retrieval_top_k,
            provider_limit,
        )

        # ---------------------------------------------------------
        # 2. France Travail
        # ---------------------------------------------------------

        raw_jobs = (
            self.provider.search_jobs(
                keywords=keywords,
                location=location,
                insee_code=insee_code,
                limit=provider_limit,
            )
        )

        # ---------------------------------------------------------
        # 3. Retrieval sémantique
        # ---------------------------------------------------------

        semantic_candidates = (
            self._semantic_retrieval(
                keywords=keywords,
                jobs=raw_jobs,
                top_k=retrieval_top_k,
            )
        )

        # ---------------------------------------------------------
        # 4. Reranking Groq
        # ---------------------------------------------------------

        llm_ranked = (
            self._llm_rerank(
                keywords=keywords,
                candidates=(
                    semantic_candidates
                ),
            )
        )

        selected = (
            llm_ranked[
                :final_limit
            ]
        )

        # ---------------------------------------------------------
        # 5. Extraction des requirements
        # ---------------------------------------------------------

        enriched_candidates = (
            self._extract_selected_jobs(
                selected
            )
        )

        # ---------------------------------------------------------
        # 6. Matching CV / offres
        # ---------------------------------------------------------

        ranked_jobs: list[
            RankedJob
        ] = []

        for (
            candidate,
            relevance_score,
            extracted_job,
        ) in enriched_candidates:

            match = (
                self.matching_engine.match(
                    cv,
                    extracted_job,
                )
            )

            explanation = (
                self.explanation_service.explain(
                    job=extracted_job,
                    match=match,
                )
            )

            ranked_jobs.append(
                RankedJob(
                    job=extracted_job,
                    match=match,
                    semantic_score=(
                        candidate.semantic_score
                    ),
                    relevance_score=(
                        relevance_score
                    ),
                    explanation=(
                        explanation
                    ),
                )
            )

        return JobRankingResult(
            candidate_name=(
                cv.candidate_name
            ),
            jobs=ranked_jobs,
        )

    # =============================================================
    # Retrieval sémantique
    # =============================================================

    def _semantic_retrieval(
            self,
            keywords: str,
            jobs: list[JobOffer],
            top_k: int,
    ) -> list[CandidateJob]:

        if not jobs:
            return []

        documents = [
            self._build_semantic_document(
                job
            )
            for job in jobs
        ]

        scores = (
            self.semantic_service.similarities(
                query=keywords,
                documents=documents,
            )
        )

        candidates = [
            CandidateJob(
                job=job,
                semantic_score=score,
            )
            for job, score in zip(
                jobs,
                scores,
                strict=True,
            )
        ]

        candidates.sort(
            key=lambda item: (
                item.semantic_score
            ),
            reverse=True,
        )

        return candidates[
            :top_k
        ]

    # =============================================================
    # Reranking Groq
    # =============================================================

    def _llm_rerank(
            self,
            keywords: str,
            candidates: list[CandidateJob],
    ) -> list[
        tuple[
            CandidateJob,
            float,
        ]
    ]:

        if not candidates:
            return []

        jobs = [
            candidate.job
            for candidate
            in candidates
        ]

        evaluations = (
            self.relevance_evaluator
            .evaluate_many(
                query=keywords,
                jobs=jobs,
            )
        )

        ranked = [
            (
                candidate,
                evaluation.relevance,
            )
            for candidate, evaluation
            in zip(
                candidates,
                evaluations,
                strict=True,
            )
        ]

        ranked.sort(
            key=lambda item: (
                item[1]
            ),
            reverse=True,
        )

        return ranked

    # =============================================================
    # Extraction requirements Groq
    # =============================================================

    def _extract_selected_jobs(
        self,
        selected: list[
            tuple[
                CandidateJob,
                float,
            ]
        ],
    ) -> list[
        tuple[
            CandidateJob,
            float,
            JobOffer,
        ]
    ]:

        if not selected:
            return []

        max_workers = min(
            self.MAX_GROQ_WORKERS,
            len(selected),
        )

        results: list[
            tuple[
                CandidateJob,
                float,
                JobOffer,
            ]
        ] = []

        def extract(
            item: tuple[
                CandidateJob,
                float,
            ],
        ) -> tuple[
            CandidateJob,
            float,
            JobOffer,
        ]:

            (
                candidate,
                relevance_score,
            ) = item

            extracted_job = (
                self._extract_job_requirements(
                    candidate.job
                )
            )

            return (
                candidate,
                relevance_score,
                extracted_job,
            )

        with ThreadPoolExecutor(
            max_workers=max_workers,
        ) as executor:

            futures = [
                executor.submit(
                    extract,
                    item,
                )
                for item
                in selected
            ]

            for future in as_completed(
                futures
            ):
                results.append(
                    future.result()
                )

        # as_completed() ne garantit pas l'ordre.
        # On restaure celui du reranking.
        position_by_key = {
            self._job_key(
                candidate.job,
                index,
            ): index
            for index, (
                candidate,
                _,
            ) in enumerate(
                selected
            )
        }

        results.sort(
            key=lambda item: (
                position_by_key.get(
                    self._job_key(
                        item[0].job,
                        0,
                    ),
                    10_000,
                )
            )
        )

        return results

    # =============================================================
    # Extraction structurée + cache + fallback
    # =============================================================

    def _extract_job_requirements(
            self,
            job: JobOffer,
    ) -> JobOffer:

        return (
            self.job_offer_extractor.extract(
                job.description or "",
                title=job.title,
                company=job.company,
                location=job.location,
                contract_type=(
                    job.contract_type
                ),
                job_id=job.id,
                source=job.source,
                source_url=job.source_url,
            )
        )

    # =============================================================
    # Retry / backoff
    # =============================================================

    @staticmethod
    def _wait_before_retry(
        attempt: int,
    ) -> None:

        delay = float(
            attempt + 1
        )

        time.sleep(
            delay
        )

    # =============================================================
    # Document pour E5
    # =============================================================

    @staticmethod
    def _build_semantic_document(
        job: JobOffer,
    ) -> str:

        parts = [
            job.title or "",
            job.description or "",
        ]

        return "\n\n".join(
            part.strip()
            for part in parts
            if (
                part
                and part.strip()
            )
        )

    # =============================================================
    # Clé stable d'offre
    # =============================================================

    @staticmethod
    def _job_key(
        job: JobOffer,
        fallback_index: int,
    ) -> str:

        if job.id:
            return str(
                job.id
            )

        return (
            f"{job.title}"
            f":{fallback_index}"
        )