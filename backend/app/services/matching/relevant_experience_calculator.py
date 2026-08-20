import re
from datetime import datetime

from app.models.cv import CV
from app.services.matching.skill_normalizer import (
    SkillNormalizer,
)


class RelevantExperienceCalculator:

    ROLE_ALIASES = {
        "machine learning": {
            "machine learning",
            "ml engineer",
            "machine learning engineer",
            "ai engineer",
            "ia engineer",
            "data scientist",
            "data science",
        },
        "data engineering": {
            "data engineer",
            "data engineering",
        },
        "backend": {
            "backend developer",
            "back-end developer",
            "développeur backend",
            "développeur back-end",
            "software engineer",
        },
        "devops": {
            "devops engineer",
            "devops",
            "mlops",
            "mlops engineer",
        },
    }

    TERM_FAMILIES = {
        "machine learning": {
            "machine learning",
            "deep learning",
            "feature engineering",
            "model training",
            "model evaluation",
            "model deployment",
            "model monitoring",
            "forecasting",
            "time series modeling",
            "computer vision",
            "nlp",
            "llm",
            "rag",
            "mlops",
            "data science",
        },
        "data engineering": {
            "data engineering",
            "etl",
            "pipeline development",
            "data pipeline",
            "spark",
            "airflow",
        },
        "backend": {
            "api",
            "rest api",
            "fastapi",
            "flask",
            "backend",
            "postgresql",
            "sql",
        },
        "devops": {
            "devops",
            "docker",
            "kubernetes",
            "ci/cd",
            "terraform",
            "aws",
            "gcp",
            "azure",
            "mlops",
        },
    }

    def calculate(
        self,
        cv: CV,
        required_terms: list[str],
    ) -> float:

        if not required_terms:
            return 0.0

        normalized_required = set(
            SkillNormalizer.normalize_many(
                required_terms
            )
        )

        required_families = (
            self._detect_required_families(
                normalized_required
            )
        )

        total_years = 0.0

        for experience in cv.experiences:
            if self._is_relevant_experience(
                experience=experience,
                normalized_required=(
                    normalized_required
                ),
                required_families=(
                    required_families
                ),
            ):
                total_years += (
                    self._calculate_duration_years(
                        experience.start_date,
                        experience.end_date,
                    )
                )

        return round(
            total_years,
            2,
        )

    def _is_relevant_experience(
        self,
        experience,
        normalized_required: set[str],
        required_families: set[str],
    ) -> bool:

        text_parts: list[str] = []

        if experience.role:
            text_parts.append(
                experience.role
            )

        text_parts.extend(
            experience.description
        )

        experience_text = " ".join(
            text_parts
        )

        found_terms = set(
            SkillNormalizer.extract_known_terms(
                experience_text
            )
        )

        # 1. Correspondance technique directe.
        if (
            found_terms
            & normalized_required
        ):
            return True

        # 2. Correspondance par famille métier.
        experience_families = (
            self._detect_experience_families(
                experience_text
            )
        )

        return bool(
            experience_families
            & required_families
        )

    @classmethod
    def _detect_required_families(
        cls,
        required_terms: set[str],
    ) -> set[str]:

        families: set[str] = set()

        for family, terms in (
            cls.TERM_FAMILIES.items()
        ):
            normalized_family_terms = {
                term.casefold()
                for term in terms
            }

            if (
                required_terms
                & normalized_family_terms
            ):
                families.add(
                    family
                )

        return families

    @classmethod
    def _detect_experience_families(
        cls,
        experience_text: str,
    ) -> set[str]:

        normalized_text = (
            experience_text.casefold()
        )

        families: set[str] = set()

        for family, aliases in (
            cls.ROLE_ALIASES.items()
        ):
            if any(
                alias.casefold()
                in normalized_text
                for alias in aliases
            ):
                families.add(
                    family
                )

        return families

    @staticmethod
    def _calculate_duration_years(
        start_date: str | None,
        end_date: str | None,
    ) -> float:

        if not start_date:
            return 0.0

        start_match = re.search(
            r"(19|20)\d{2}",
            start_date,
        )

        if not start_match:
            return 0.0

        start_year = int(
            start_match.group()
        )

        if end_date:
            end_match = re.search(
                r"(19|20)\d{2}",
                end_date,
            )
        else:
            end_match = None

        if end_match:
            end_year = int(
                end_match.group()
            )
        else:
            end_year = datetime.now().year

        if end_year < start_year:
            return 0.0

        return float(
            end_year
            - start_year
        )