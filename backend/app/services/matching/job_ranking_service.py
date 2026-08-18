from app.models.cv import CV
from app.models.job import JobOffer
from app.models.ranking import (
    JobRankingResult,
    RankedJob,
)
from app.services.jobs.job_offer_extractor import (
    JobOfferExtractor,
)
from app.services.matching.matching_engine import (
    MatchingEngine,
)


class JobRankingService:

    def __init__(self):
        self.job_offer_extractor = JobOfferExtractor()
        self.matching_engine = MatchingEngine()

    def rank(
        self,
        cv: CV,
        jobs: list[JobOffer],
    ) -> JobRankingResult:

        ranked_jobs: list[RankedJob] = []

        for job in jobs:

            # Les offres venant du provider possèdent déjà
            # leurs métadonnées. On enrichit leurs exigences
            # à partir de la description.
            extracted_job = self.job_offer_extractor.extract(
                text=job.description,
                title=job.title,
                company=job.company,
                location=job.location,
                contract_type=job.contract_type,
            )

            # On conserve les informations provenant
            # du provider.
            extracted_job.id = job.id
            extracted_job.source = job.source
            extracted_job.source_url = job.source_url

            match = self.matching_engine.match(
                cv,
                extracted_job,
            )

            ranked_jobs.append(
                RankedJob(
                    job=extracted_job,
                    match=match,
                )
            )

        ranked_jobs.sort(
            key=lambda item: item.match.score,
            reverse=True,
        )

        return JobRankingResult(
            candidate_name=cv.candidate_name,
            jobs=ranked_jobs,
        )