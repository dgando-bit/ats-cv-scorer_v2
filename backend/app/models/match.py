# app/models/match.py

from pydantic import BaseModel, Field


class MatchDetails(BaseModel):
    skills: float = 0.0
    tools: float = 0.0
    languages: float = 0.0
    experience: float = 0.0
    education: float = 0.0


class MatchResult(BaseModel):
    score: float

    details: MatchDetails

    matched_skills: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    matched_tools: list[str] = Field(
        default_factory=list
    )

    missing_tools: list[str] = Field(
        default_factory=list
    )

    matched_languages: list[str] = Field(
        default_factory=list
    )

    missing_languages: list[str] = Field(
        default_factory=list
    )