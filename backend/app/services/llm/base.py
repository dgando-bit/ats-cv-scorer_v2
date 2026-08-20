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