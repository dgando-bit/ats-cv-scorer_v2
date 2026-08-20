import pytest
from pydantic import ValidationError

from app.models.job_requirements import (
    ExperienceRequirement,
    JobRequirements,
    LanguageRequirement,
)


def test_job_requirements():
    requirements = JobRequirements(
        hard_skills=[
            "machine learning",
            "feature engineering",
        ],
        tools=[
            "Python",
            "AWS",
        ],
        soft_skills=[
            "autonomie",
        ],
        languages=[
            LanguageRequirement(
                language="anglais",
                level="B2",
            )
        ],
        experience=ExperienceRequirement(
            min_years=2,
            max_years=4,
        ),
        education_level="Bac+5",
        certifications=[],
        responsibilities=[
            "Développer des modèles ML",
        ],
    )

    assert requirements.hard_skills == [
        "machine learning",
        "feature engineering",
    ]

    assert requirements.tools == [
        "Python",
        "AWS",
    ]

    assert requirements.languages[0].language == (
        "anglais"
    )

    assert requirements.languages[0].level == "B2"

    assert requirements.experience.min_years == 2
    assert requirements.experience.max_years == 4

    assert requirements.education_level == "Bac+5"


def test_job_requirements_can_represent_missing_requirements():
    requirements = JobRequirements(
        hard_skills=[],
        tools=[],
        soft_skills=[],
        languages=[],
        experience=ExperienceRequirement(
            min_years=None,
            max_years=None,
        ),
        education_level=None,
        certifications=[],
        responsibilities=[],
    )

    assert requirements.hard_skills == []
    assert requirements.tools == []
    assert requirements.soft_skills == []
    assert requirements.languages == []

    assert (
        requirements.experience.min_years
        is None
    )

    assert (
        requirements.experience.max_years
        is None
    )

    assert requirements.education_level is None

def test_experience_cannot_be_negative():
    with pytest.raises(ValidationError):
        ExperienceRequirement(
            min_years=-1,
            max_years=None,
        )