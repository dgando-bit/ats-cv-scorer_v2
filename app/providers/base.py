from abc import ABC, abstractmethod

from app.models.job import JobOffer


class JobProvider(ABC):

    @abstractmethod
    def search(
        self,
        query: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[JobOffer]:
        """Search job offers."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        job_id: str,
    ) -> JobOffer | None:
        """Retrieve one job offer."""
        raise NotImplementedError