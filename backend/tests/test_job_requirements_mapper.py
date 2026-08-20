from app.models.job import JobOffer
from app.models.job_requirements import (
    ExperienceRequirement,
    JobRequirements,
    LanguageRequirement,
)
from app.services.jobs.job_requirements_mapper import (
    JobRequirementsMapper,
)


def test_map_job_requirements_to_job_offer():
    source_job = JobOffer(
        id="123",
        title="AI Engineer",
        company="ACME",
        location="75 - Paris",
        contract_type="CDI",
        description="Test description",
        source="france_travail",
        source_url="https://example.com",
    )

    requirements = JobRequirements(
        hard_skills=[
            "machine learning",
            "Python",
        ],
        tools=[
            "AWS",
        ],
        soft_skills=[
            "autonomie",
        ],
        languages=[
            LanguageRequirement(
                language="French",
                level="native",
            ),
            LanguageRequirement(
                language="English",
                level="B2",
            ),
        ],
        experience=ExperienceRequirement(
            min_years=2,
            max_years=4,
        ),
        education_level="Master",
        certifications=[],
        responsibilities=[
            "Develop ML models",
        ],
    )

    result = JobRequirementsMapper.to_job_offer(
        source_job=source_job,
        requirements=requirements,
    )

    assert result.id == "123"
    assert result.title == "AI Engineer"
    assert result.company == "ACME"
    assert result.location == "75 - Paris"
    assert result.contract_type == "CDI"
    assert result.description == "Test description"

    assert "machine learning" in result.skills
    assert "Python" in result.skills

    assert result.tools == [
        "AWS",
    ]

    assert result.soft_skills == [
        "autonomie",
    ]

    assert result.languages == [
        "French (native)",
        "English (B2)",
    ]

    assert (
        result.experience_required
        == "2 à 4 ans"
    )

    assert (
        result.education_required
        == "Master"
    )

    assert (
        result.source
        == "france_travail"
    )

    assert (
        result.source_url
        == "https://example.com"
    )


def test_map_open_ended_experience():
    source_job = JobOffer(
        title="Developer",
        description="",
    )

    requirements = JobRequirements(
        hard_skills=[],
        tools=[],
        soft_skills=[],
        languages=[],
        experience=ExperienceRequirement(
            min_years=3,
            max_years=None,
        ),
        education_level=None,
        certifications=[],
        responsibilities=[],
    )

    result = JobRequirementsMapper.to_job_offer(
        source_job=source_job,
        requirements=requirements,
    )

    assert (
        result.experience_required
        == "3 ans"
    )


def test_map_missing_experience():
    source_job = JobOffer(
        title="Developer",
        description="",
    )

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

    result = JobRequirementsMapper.to_job_offer(
        source_job=source_job,
        requirements=requirements,
    )

    assert result.experience_required is None