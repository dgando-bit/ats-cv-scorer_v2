from dataclasses import dataclass

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
from app.services.llm.base import (
	JobRelevanceEvaluator,
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
from app.services.jobs.job_requirements_mapper import (
	JobRequirementsMapper,
)
from app.services.llm.groq_job_requirements_extractor import (
	GroqJobRequirementsExtractor,
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
			requirements_extractor: GroqJobRequirementsExtractor | None = None,
			matching_engine: MatchingEngine | None = None,
			explanation_service: MatchExplanationService | None = None,
	) -> None:
		self.provider = provider
		self.relevance_evaluator = relevance_evaluator

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

	def search_and_rank(
			self,
			cv: CV,
			keywords: str,
			location: str | None = None,
			insee_code: str | None = None,
			provider_limit: int = 50,
			retrieval_top_k: int = 20,
			final_limit: int = 10,
	) -> JobRankingResult:

		raw_jobs = self.provider.search_jobs(
			keywords=keywords,
			location=location,
			insee_code=insee_code,
			limit=provider_limit,
		)

		semantic_candidates = (
			self._semantic_retrieval(
				keywords=keywords,
				jobs=raw_jobs,
				top_k=retrieval_top_k,
			)
		)

		llm_ranked = (
			self._llm_rerank(
				keywords=keywords,
				candidates=semantic_candidates,
			)
		)

		selected = llm_ranked[
			:final_limit
		]

		ranked_jobs: list[RankedJob] = []

		for (
				candidate,
				relevance_score,
		) in selected:
			extracted_job = (
				self._extract_job_requirements(
					candidate.job
				)
			)

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
					explanation=explanation,
				)
			)

		return JobRankingResult(
			candidate_name=cv.candidate_name,
			jobs=ranked_jobs,
		)

	def _semantic_retrieval(
			self,
			keywords: str,
			jobs: list[JobOffer],
			top_k: int,
	) -> list[CandidateJob]:

		candidates = []

		for job in jobs:
			document = (
				self._build_semantic_document(
					job
				)
			)

			score = (
				self.semantic_service.similarity(
					query=keywords,
					document=document,
				)
			)

			candidates.append(
				CandidateJob(
					job=job,
					semantic_score=score,
				)
			)

		candidates.sort(
			key=lambda item: (
				item.semantic_score
			),
			reverse=True,
		)

		return candidates[:top_k]

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

		ranked = []

		for candidate in candidates:
			evaluation = (
				self.relevance_evaluator.evaluate(
					query=keywords,
					job=candidate.job,
				)
			)

			ranked.append(
				(
					candidate,
					evaluation.relevance,
				)
			)

		ranked.sort(
			key=lambda item: item[1],
			reverse=True,
		)

		return ranked

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
			if part
			and part.strip()
		)

	def _extract_job_requirements(
			self,
			job: JobOffer,
	) -> JobOffer:
		try:
			requirements = (
				self.requirements_extractor.extract(
					job
				)
			)

			return JobRequirementsMapper.to_job_offer(
				source_job=job,
				requirements=requirements,
			)

		except Exception:
			return self.job_offer_extractor.extract(
				job.description or "",
				title=job.title,
				company=job.company,
				location=job.location,
				contract_type=job.contract_type,
				job_id=job.id,
				source=job.source,
				source_url=job.source_url,
			)
