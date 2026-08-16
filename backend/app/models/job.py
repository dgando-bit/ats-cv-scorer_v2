# app/models/job.py

from pydantic import BaseModel, Field


class JobOffer(BaseModel):
    id: str | None = None

    title: str

    company: str | None = None

    location: str | None = None

    contract_type: str | None = None

    description: str

    skills: list[str] = Field(
        default_factory=list
    )

    tools: list[str] = Field(
        default_factory=list
    )

    soft_skills: list[str] = Field(
        default_factory=list
    )

    languages: list[str] = Field(
        default_factory=list
    )

    experience_required: str | None = None

    education_required: str | None = None

    source: str | None = None

    source_url: str | None = None