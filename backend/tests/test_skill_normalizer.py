from app.services.matching.skill_normalizer import (
    SkillNormalizer,
)


def test_normalize_known_aliases():
    assert (
        SkillNormalizer.normalize("sklearn")
        == "scikit-learn"
    )

    assert (
        SkillNormalizer.normalize("Postgres")
        == "postgresql"
    )

    assert (
        SkillNormalizer.normalize("ML")
        == "machine learning"
    )

    assert (
        SkillNormalizer.normalize("K8s")
        == "kubernetes"
    )


def test_normalize_unknown_skill():
    assert (
        SkillNormalizer.normalize("FastAPI")
        == "fastapi"
    )


def test_normalize_many_removes_duplicates():
    values = [
        "sklearn",
        "Scikit-Learn",
        "Postgres",
        "PostgreSQL",
    ]

    result = SkillNormalizer.normalize_many(
        values
    )

    assert result == [
        "scikit-learn",
        "postgresql",
    ]