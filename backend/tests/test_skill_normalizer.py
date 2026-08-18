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

def test_extract_known_terms_from_composite_skill():

    result = SkillNormalizer.extract_known_terms(
        "Modélisation ML (Scikit-learn)"
    )

    assert "machine learning" in result
    assert "scikit-learn" in result

def test_extract_multiple_tools_from_same_value():

    result = SkillNormalizer.extract_known_terms(
        "GCP / AWS"
    )

    assert "gcp" in result
    assert "aws" in result

def test_extract_tools_inside_parentheses():

    result = SkillNormalizer.extract_known_terms(
        "PyTorch (ou TensorFlow)"
    )

    assert "pytorch" in result
    assert "tensorflow" in result