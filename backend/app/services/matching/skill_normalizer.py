import re


class SkillNormalizer:

    ALIASES = {
        "sklearn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "postgres": "postgresql",
        "postgre": "postgresql",
        "ml": "machine learning",
        "machine-learning": "machine learning",
        "dl": "deep learning",
        "deep-learning": "deep learning",
        "k8s": "kubernetes",
        "py torch": "pytorch",
        "tf": "tensorflow",
        "amazon web services": "aws",
        "google cloud platform": "gcp",
    }

    KNOWN_TERMS = {
        "python",
        "sql",
        "machine learning",
        "deep learning",
        "data engineering",
        "data science",
        "computer vision",
        "nlp",
        "llm",
        "rag",
        "mlops",
        "pandas",
        "numpy",
        "scikit-learn",
        "pytorch",
        "tensorflow",
        "docker",
        "kubernetes",
        "git",
        "postgresql",
        "mlflow",
        "dvc",
        "airflow",
        "fastapi",
        "flask",
        "aws",
        "gcp",
        "azure",
        "spark",
    }

    @classmethod
    def normalize(cls, value: str) -> str:
        normalized = (
            value.strip()
            .lower()
        )

        return cls.ALIASES.get(
            normalized,
            normalized,
        )

    @classmethod
    def normalize_many(
        cls,
        values: list[str],
    ) -> list[str]:

        normalized = [
            cls.normalize(value)
            for value in values
        ]

        return list(
            dict.fromkeys(normalized)
        )

    @classmethod
    def extract_known_terms(
        cls,
        text: str,
    ) -> list[str]:

        normalized_text = text.lower()

        found: list[str] = []

        # 1. Chercher les termes canoniques
        for term in cls.KNOWN_TERMS:

            if re.search(
                rf"\b{re.escape(term)}\b",
                normalized_text,
                flags=re.IGNORECASE,
            ):
                found.append(term)

        # 2. Chercher les alias
        for alias, canonical in cls.ALIASES.items():

            if re.search(
                rf"\b{re.escape(alias)}\b",
                normalized_text,
                flags=re.IGNORECASE,
            ):
                found.append(canonical)

        return list(
            dict.fromkeys(found)
        )