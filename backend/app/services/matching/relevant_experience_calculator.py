import re
from datetime import datetime

from app.models.cv import CV
from app.services.matching.skill_normalizer import SkillNormalizer


class RelevantExperienceCalculator:

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

        total_years = 0.0

        for experience in cv.experiences:

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

            if not (
                found_terms
                & normalized_required
            ):
                continue

            duration = self._calculate_duration_years(
                experience.start_date,
                experience.end_date,
            )

            total_years += duration

        return round(
            total_years,
            2,
        )

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
            end_year - start_year
        )