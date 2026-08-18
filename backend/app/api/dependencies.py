from app.providers.base import JobProvider
from app.providers.france_travail import FranceTravailProvider


def get_job_provider() -> JobProvider:
    return FranceTravailProvider()