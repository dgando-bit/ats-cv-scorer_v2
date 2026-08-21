from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class BatchJobRelevanceItem(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    candidate_id: str

    relevance: float = Field(
        ge=0.0,
        le=1.0,
    )

    reason: str


class BatchJobRelevanceResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    evaluations: list[
        BatchJobRelevanceItem
    ]