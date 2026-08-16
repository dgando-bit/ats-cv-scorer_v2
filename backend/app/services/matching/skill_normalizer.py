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

        return list(dict.fromkeys(normalized))