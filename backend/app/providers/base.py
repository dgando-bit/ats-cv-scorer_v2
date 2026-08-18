from abc import ABC, abstractmethod

from app.models.job import JobOffer


class JobProvider(ABC):

    @abstractmethod
    def search_jobs(
        self,
        keywords: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[JobOffer]:
        raise NotImplementedError