from app.models.job_requirements import (
    ExperienceRequirement,
    JobRequirements,
)
from app.services.jobs.job_requirements_normalizer import (
    JobRequirementsNormalizer,
)


def make_requirements(
    *,
    hard_skills: list[str] | None = None,
    tools: list[str] | None = None,
) -> JobRequirements:
    return JobRequirements(
        hard_skills=hard_skills or [],
        tools=tools or [],
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


def test_moves_technologies_from_skills_to_tools():
    requirements = make_requirements(
        hard_skills=[
            "Python",
            "PyTorch",
            "Machine Learning",
            "Computer Vision",
        ]
    )

    result = (
        JobRequirementsNormalizer.normalize(
            requirements
        )
    )

    assert result.hard_skills == [
        "Machine Learning",
        "Computer Vision",
    ]

    assert result.tools == [
        "Python",
        "PyTorch",
    ]


def test_removes_duplicate_tools():
    requirements = make_requirements(
        hard_skills=[
            "Docker",
            "MLflow",
        ],
        tools=[
            "Docker",
            "MLflow",
            "Git",
        ],
    )

    result = (
        JobRequirementsNormalizer.normalize(
            requirements
        )
    )

    assert result.tools == [
        "Docker",
        "MLflow",
        "Git",
    ]


def test_removes_non_tools():
    requirements = make_requirements(
        tools=[
            "Git",
            "testing",
            "Code-Review",
        ]
    )

    result = (
        JobRequirementsNormalizer.normalize(
            requirements
        )
    )

    assert result.tools == [
        "Git",
    ]


def test_moves_skill_from_tools_to_skills():
    requirements = make_requirements(
        tools=[
            "Docker",
            "MLOps",
        ]
    )

    result = (
        JobRequirementsNormalizer.normalize(
            requirements
        )
    )

    assert result.hard_skills == [
        "MLOps",
    ]

    assert result.tools == [
        "Docker",
    ]


def test_normalizes_aliases():
    requirements = make_requirements(
        hard_skills=[
            "retrieval-augmented generation",
        ],
        tools=[
            "sklearn",
        ],
    )

    result = (
        JobRequirementsNormalizer.normalize(
            requirements
        )
    )

    assert result.hard_skills == [
        "RAG",
    ]

    assert result.tools == [
        "Scikit-learn",
    ]


def test_preserves_unknown_domain_skill():
    requirements = make_requirements(
        hard_skills=[
            "3D mesh segmentation",
        ]
    )

    result = (
        JobRequirementsNormalizer.normalize(
            requirements
        )
    )

    assert result.hard_skills == [
        "3D mesh segmentation",
    ]