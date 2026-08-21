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
from app.services.llm.groq_job_requirements_batch_extractor import (
    GroqJobRequirementsBatchExtractor,
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
    def __init__(
        self,
        provider: JobProvider,
        relevance_evaluator: JobRelevanceEvaluator,
        semantic_service: SemanticSimilarityService | None = None,
        job_offer_extractor: JobOfferExtractor | None = None,
        requirements_batch_extractor: (
            GroqJobRequirementsBatchExtractor | None
        ) = None,
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

        self.requirements_batch_extractor = (
            requirements_batch_extractor
            or GroqJobRequirementsBatchExtractor()
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
        # Cache mémoire des offres enrichies
        # ---------------------------------------------------------

        self._requirements_cache: dict[
            str,
            JobOffer,
        ] = {}

        self._requirements_cache_lock = (
            Lock()
        )

    # =============================================================
    # Pipeline principal
    # =============================================================

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
        # 1. Normalisation des limites
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
        # 2. Recherche France Travail
        # ---------------------------------------------------------

        raw_jobs = (
            self.provider.search_jobs(
                keywords=keywords,
                location=location,
                insee_code=insee_code,
                limit=provider_limit,
            )
        )

        if not raw_jobs:
            return JobRankingResult(
                candidate_name=(
                    cv.candidate_name
                ),
                jobs=[],
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
        #
        # Si Groq est indisponible ou rate-limité,
        # on conserve simplement l'ordre sémantique.
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
        # 5. Extraction batch des requirements
        #
        # En cas d'échec Groq :
        # fallback lexical local.
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
    # Reranking Groq avec fallback
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

        try:
            print(
                "[rerank] "
                f"Sending {len(jobs)} jobs to Groq...",
                flush=True,
            )

            evaluations = (
                self.relevance_evaluator
                .evaluate_many(
                    query=keywords,
                    jobs=jobs,
                )
            )

            if (
                len(evaluations)
                != len(candidates)
            ):
                raise ValueError(
                    "Relevance batch size "
                    "does not match candidate "
                    "batch size."
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

            print(
                "[rerank] "
                "Groq reranking completed.",
                flush=True,
            )

            return ranked

        except RateLimitError as exc:
            print(
                "[rerank] "
                "Groq rate limit reached. "
                "Falling back to semantic ranking.",
                flush=True,
            )

            print(
                "[rerank] "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )

            return (
                self._semantic_ranking_fallback(
                    candidates
                )
            )

        except Exception as exc:
            print(
                "[rerank] "
                "Groq reranking failed. "
                "Falling back to semantic ranking.",
                flush=True,
            )

            print(
                "[rerank] "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )

            return (
                self._semantic_ranking_fallback(
                    candidates
                )
            )

    # =============================================================
    # Fallback du reranking
    # =============================================================

    @staticmethod
    def _semantic_ranking_fallback(
        candidates: list[CandidateJob],
    ) -> list[
        tuple[
            CandidateJob,
            float,
        ]
    ]:
        """
        Le retrieval sémantique a déjà trié les candidats
        par semantic_score décroissant.

        En cas d'échec du LLM, on utilise donc directement
        ce classement.

        Le relevance_score est alors égal au semantic_score
        afin de conserver une valeur exploitable côté frontend.
        """

        return [
            (
                candidate,
                candidate.semantic_score,
            )
            for candidate in candidates
        ]

    # =============================================================
    # Extraction BATCH des requirements
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

        enriched_jobs: list[
            JobOffer | None
        ] = [
            None
        ] * len(selected)

        missing_jobs: list[
            JobOffer
        ] = []

        missing_positions: list[
            int
        ] = []

        # ---------------------------------------------------------
        # 1. Cache
        # ---------------------------------------------------------

        for index, (
            candidate,
            _,
        ) in enumerate(selected):

            key = self._job_key(
                candidate.job,
                index,
            )

            with (
                self
                ._requirements_cache_lock
            ):
                cached = (
                    self
                    ._requirements_cache
                    .get(key)
                )

            if cached is not None:
                print(
                    "[requirements-batch] "
                    f"Cache hit for job {key}",
                    flush=True,
                )

                enriched_jobs[
                    index
                ] = cached

                continue

            missing_jobs.append(
                candidate.job
            )

            missing_positions.append(
                index
            )

        # ---------------------------------------------------------
        # 2. Groq batch
        # ---------------------------------------------------------

        if missing_jobs:
            try:
                print(
                    "[requirements-batch] "
                    f"Sending {len(missing_jobs)} "
                    "jobs to Groq...",
                    flush=True,
                )

                requirements_list = (
                    self
                    .requirements_batch_extractor
                    .extract(
                        missing_jobs
                    )
                )

                print(
                    "[requirements-batch] "
                    f"Groq returned "
                    f"{len(requirements_list)} "
                    "requirements.",
                    flush=True,
                )

                if (
                    len(requirements_list)
                    != len(missing_jobs)
                ):
                    raise ValueError(
                        "Requirements batch size "
                        "does not match jobs batch "
                        "size."
                    )

                for (
                    position,
                    source_job,
                    requirements,
                ) in zip(
                    missing_positions,
                    missing_jobs,
                    requirements_list,
                    strict=True,
                ):

                    enriched_job = (
                        JobRequirementsMapper
                        .to_job_offer(
                            source_job=(
                                source_job
                            ),
                            requirements=(
                                requirements
                            ),
                        )
                    )

                    enriched_jobs[
                        position
                    ] = enriched_job

                    key = self._job_key(
                        source_job,
                        position,
                    )

                    with (
                        self
                        ._requirements_cache_lock
                    ):
                        (
                            self
                            ._requirements_cache[
                                key
                            ]
                        ) = enriched_job

                print(
                    "[requirements-batch] "
                    "Batch extraction completed "
                    "successfully.",
                    flush=True,
                )

            except RateLimitError as exc:
                print(
                    "[requirements-batch] "
                    "Groq rate limit reached. "
                    "Using lexical fallback.",
                    flush=True,
                )

                print(
                    "[requirements-batch] "
                    f"{type(exc).__name__}: {exc}",
                    flush=True,
                )

                self._apply_lexical_fallback(
                    missing_jobs=missing_jobs,
                    missing_positions=(
                        missing_positions
                    ),
                    enriched_jobs=(
                        enriched_jobs
                    ),
                )

            except Exception as exc:
                print(
                    "[requirements-batch] "
                    "Groq extraction failed. "
                    "Using lexical fallback.",
                    flush=True,
                )

                print(
                    "[requirements-batch] "
                    f"{type(exc).__name__}: {exc}",
                    flush=True,
                )

                self._apply_lexical_fallback(
                    missing_jobs=missing_jobs,
                    missing_positions=(
                        missing_positions
                    ),
                    enriched_jobs=(
                        enriched_jobs
                    ),
                )

        # ---------------------------------------------------------
        # 3. Reconstruction du résultat
        # ---------------------------------------------------------

        results: list[
            tuple[
                CandidateJob,
                float,
                JobOffer,
            ]
        ] = []

        for index, (
            candidate,
            relevance_score,
        ) in enumerate(selected):

            extracted_job = (
                enriched_jobs[
                    index
                ]
            )

            if extracted_job is None:
                extracted_job = (
                    self
                    ._extract_job_requirements_fallback(
                        candidate.job
                    )
                )

            results.append(
                (
                    candidate,
                    relevance_score,
                    extracted_job,
                )
            )

        return results

    # =============================================================
    # Application du fallback lexical
    # =============================================================

    def _apply_lexical_fallback(
        self,
        missing_jobs: list[JobOffer],
        missing_positions: list[int],
        enriched_jobs: list[
            JobOffer | None
        ],
    ) -> None:

        print(
            "[requirements-batch] "
            "Using lexical fallback "
            f"for {len(missing_jobs)} jobs.",
            flush=True,
        )

        for (
            position,
            source_job,
        ) in zip(
            missing_positions,
            missing_jobs,
            strict=True,
        ):

            enriched_job = (
                self
                ._extract_job_requirements_fallback(
                    source_job
                )
            )

            enriched_jobs[
                position
            ] = enriched_job

            key = self._job_key(
                source_job,
                position,
            )

            with (
                self
                ._requirements_cache_lock
            ):
                (
                    self
                    ._requirements_cache[
                        key
                    ]
                ) = enriched_job

    # =============================================================
    # Fallback lexical
    # =============================================================

    def _extract_job_requirements_fallback(
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