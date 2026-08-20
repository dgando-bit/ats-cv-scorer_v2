from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class LanguageRequirement(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    language: str
    level: str | None


class ExperienceRequirement(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    min_years: float | None = Field(
        ge=0,
    )

    max_years: float | None = Field(
        ge=0,
    )

    context: str | None


class JobRequirements(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    hard_skills: list[str]
    tools: list[str]
    soft_skills: list[str]
    languages: list[LanguageRequirement]

    experience: ExperienceRequirement

    education_level: str | None

    certifications: list[str]

    responsibilities: list[str]