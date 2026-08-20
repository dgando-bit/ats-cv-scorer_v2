from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class JobRelevanceEvaluation(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    relevance: float = Field(
        ge=0.0,
        le=1.0,
    )

    reason: str