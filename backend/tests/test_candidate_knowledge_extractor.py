from app.models.cv import (
    CV,
    Contact,
    Experience,
)

from app.services.matching.candidate_knowledge_extractor import (
    CandidateKnowledgeExtractor,
)


def test_extract_candidate_knowledge_from_cv():

    cv = CV(
        candidate_name="John Doe",
        title="Machine Learning Engineer",
        contact=Contact(),
        profile=(
            "Machine Learning Engineer "
            "avec expérience MLOps."
        ),
        experiences=[
            Experience(
                company="ACME",
                role="ML Engineer",
                start_date="2022",
                end_date="2025",
                description=[
                    (
                        "Data Engineering avec "
                        "Python et Airflow."
                    ),
                    (
                        "Computer Vision et "
                        "Data Science."
                    ),
                ],
            ),
        ],
        education=[],
        skills=[
            "Modélisation ML (Scikit-learn)",
            "LLM",
            "RAG",
        ],
        soft_skills=[],
        tools=[
            "GCP / AWS",
            "PyTorch (ou TensorFlow)",
            "Docker",
        ],
        languages=[],
    )

    extractor = CandidateKnowledgeExtractor()

    result = extractor.extract(cv)

    assert "machine learning" in result.terms
    assert "scikit-learn" in result.terms
    assert "llm" in result.terms
    assert "rag" in result.terms

    assert "gcp" in result.terms
    assert "aws" in result.terms
    assert "pytorch" in result.terms
    assert "tensorflow" in result.terms
    assert "docker" in result.terms

    assert "mlops" in result.terms
    assert "data engineering" in result.terms
    assert "computer vision" in result.terms
    assert "data science" in result.terms
    assert "python" in result.terms
    assert "airflow" in result.terms