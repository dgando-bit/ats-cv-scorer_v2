from pydantic import BaseModel, Field

from app.models.job import JobOffer
from app.models.match import MatchExplanation, MatchResult


class RankedJob(BaseModel):
    job: JobOffer
    match: MatchResult

    semantic_score: float | None = None
    relevance_score: float

    explanation: MatchExplanation


class JobRankingResult(BaseModel):
    candidate_name: str | None = None

    jobs: list[RankedJob] = Field(
        default_factory=list
    )