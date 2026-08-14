from fastapi import APIRouter
from pydantic import BaseModel

from app.models.cv import CV
from app.models.job import JobOffer
from app.models.match import MatchResult
from app.services.matching_engine import MatchingEngine


router = APIRouter(
    prefix="/api",
    tags=["matching"],
)


class MatchRequest(BaseModel):
    cv: CV
    job: JobOffer


matching_engine = MatchingEngine()


@router.post(
    "/match",
    response_model=MatchResult,
)
def match_cv_job(
    payload: MatchRequest,
) -> MatchResult:

    return matching_engine.match(
        payload.cv,
        payload.job,
    )