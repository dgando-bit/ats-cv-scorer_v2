from abc import ABC, abstractmethod

from app.models.job import JobOffer
from app.models.job_relevance import (
    JobRelevanceEvaluation,
)


class JobRelevanceEvaluator(ABC):

    @abstractmethod
    def evaluate(
        self,
        query: str,
        job: JobOffer,
    ) -> JobRelevanceEvaluation:
        pass

    def evaluate_many(
        self,
        query: str,
        jobs: list[JobOffer],
    ) -> list[
        JobRelevanceEvaluation
    ]:
        """
        Fallback générique.

        Les implémentations ne supportant pas le batch
        continuent à fonctionner en appelant evaluate()
        pour chaque offre.

        GroqJobRelevanceEvaluator surcharge cette méthode
        avec un véritable appel batch.
        """

        return [
            self.evaluate(
                query=query,
                job=job,
            )
            for job in jobs
        ]