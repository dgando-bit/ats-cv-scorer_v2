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
            "Machine Learning",
            "RAG",
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
                language="English",
                level="B2",
            ),
        ],
        experience=ExperienceRequirement(
            min_years=2,
            max_years=4,
            context="Machine Learning",
        ),
        education_level="Bac+5",
        certifications=[],
        responsibilities=[
            "Développer des modèles ML",
        ],
    )

    assert requirements.hard_skills == [
        "Machine Learning",
        "RAG",
    ]

    assert requirements.tools == [
        "Python",
        "AWS",
    ]

    assert requirements.soft_skills == [
        "autonomie",
    ]

    assert (
        requirements.languages[0].language
        == "English"
    )

    assert (
        requirements.languages[0].level
        == "B2"
    )

    assert (
        requirements.experience.min_years
        == 2
    )

    assert (
        requirements.experience.max_years
        == 4
    )

    assert (
        requirements.experience.context
        == "Machine Learning"
    )

    assert (
        requirements.education_level
        == "Bac+5"
    )

    assert requirements.certifications == []

    assert requirements.responsibilities == [
        "Développer des modèles ML",
    ]


def test_job_requirements_can_represent_missing_requirements():
    requirements = JobRequirements(
        hard_skills=[],
        tools=[],
        soft_skills=[],
        languages=[],
        experience=ExperienceRequirement(
            min_years=None,
            max_years=None,
            context=None,
        ),
        education_level=None,
        certifications=[],
        responsibilities=[],
    )

    assert requirements.hard_skills == []
    assert requirements.tools == []
    assert requirements.soft_skills == []
    assert requirements.languages == []
    assert requirements.certifications == []
    assert requirements.responsibilities == []

    assert (
        requirements.experience.min_years
        is None
    )

    assert (
        requirements.experience.max_years
        is None
    )

    assert (
        requirements.experience.context
        is None
    )

    assert (
        requirements.education_level
        is None
    )


def test_experience_cannot_be_negative():
    with pytest.raises(
        ValidationError
    ):
        ExperienceRequirement(
            min_years=-1,
            max_years=None,
            context=None,
        )


def test_experience_context_is_preserved():
    requirement = ExperienceRequirement(
        min_years=2,
        max_years=3,
        context="Lead Machine Learning",
    )

    assert (
        requirement.context
        == "Lead Machine Learning"
    )