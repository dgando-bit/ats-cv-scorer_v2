from pydantic import BaseModel, Field

from app.models.job import JobOffer
from app.models.match import MatchResult


class RankedJob(BaseModel):
    job: JobOffer
    match: MatchResult


class JobRankingResult(BaseModel):
    candidate_name: str | None = None

    jobs: list[RankedJob] = Field(
        default_factory=list
    )