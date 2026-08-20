from app.models.job_requirements import (
    JobRequirements,
)


class JobRequirementsNormalizer:
    """
    Normalise les exigences extraites par le LLM.

    Objectifs :
    - séparer les compétences métier des technologies ;
    - supprimer les doublons ;
    - canonicaliser les noms courants ;
    - retirer des tools les pratiques qui ne sont
      pas réellement des outils.
    """

    TOOL_ALIASES = {
        "python": "Python",
        "sql": "SQL",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "scikit-learn": "Scikit-learn",
        "sklearn": "Scikit-learn",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "fastapi": "FastAPI",
        "flask": "Flask",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "git": "Git",
        "mlflow": "MLflow",
        "dvc": "DVC",
        "airflow": "Airflow",
        "spark": "Spark",
        "postgresql": "PostgreSQL",
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "GCP",
        "terraform": "Terraform",
        "triton inference server": (
            "Triton Inference Server"
        ),
    }

    SKILL_ALIASES = {
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "computer vision": "Computer Vision",
        "nlp": "NLP",
        "natural language processing": "NLP",
        "rag": "RAG",
        "retrieval augmented generation": "RAG",
        "retrieval-augmented generation": "RAG",
        "llm": "LLM",
        "large language models": "LLM",
        "data science": "Data Science",
        "data engineering": "Data Engineering",
        "mlops": "MLOps",
    }

    NON_TOOLS = {
        "testing",
        "code-review",
        "code review",
        "unit testing",
        "software testing",
    }

    @classmethod
    def normalize(
        cls,
        requirements: JobRequirements,
    ) -> JobRequirements:
        skills: list[str] = []
        tools: list[str] = []

        for value in requirements.hard_skills:
            normalized = cls._normalize_value(
                value
            )

            key = normalized.lower()

            if key in cls.TOOL_ALIASES:
                tools.append(
                    cls.TOOL_ALIASES[key]
                )
                continue

            skills.append(
                cls.SKILL_ALIASES.get(
                    key,
                    normalized,
                )
            )

        for value in requirements.tools:
            normalized = cls._normalize_value(
                value
            )

            key = normalized.lower()

            if key in cls.NON_TOOLS:
                continue

            if key in cls.SKILL_ALIASES:
                skills.append(
                    cls.SKILL_ALIASES[key]
                )
                continue

            tools.append(
                cls.TOOL_ALIASES.get(
                    key,
                    normalized,
                )
            )

        return requirements.model_copy(
            update={
                "hard_skills": cls._unique(
                    skills
                ),
                "tools": cls._unique(
                    tools
                ),
            }
        )

    @staticmethod
    def _normalize_value(
        value: str,
    ) -> str:
        return " ".join(
            value.strip().split()
        )

    @staticmethod
    def _unique(
        values: list[str],
    ) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for value in values:
            key = value.casefold()

            if key in seen:
                continue

            seen.add(key)
            result.append(value)

        return result