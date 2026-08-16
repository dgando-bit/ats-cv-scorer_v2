import re
from app.models.cv import CV
from app.models.job import JobOffer
from app.services.matching.skill_normalizer import SkillNormalizer
from datetime import datetime
from app.models.match import MatchDetails, MatchResult

class MatchingEngine:

    WEIGHTS = {
        "skills": 0.40,
        "tools": 0.25,
        "languages": 0.10,
        "experience": 0.15,
        "education": 0.10,
    }

    EDUCATION_LEVELS = {
        "bts": 2,
        "bac+2": 2,
        "bac +2": 2,
        "bachelor": 3,
        "licence": 3,
        "bac+3": 3,
        "bac +3": 3,
        "master": 5,
        "bac+5": 5,
        "bac +5": 5,
        "doctorat": 8,
        "phd": 8,
        "bac+8": 8,
        "bac +8": 8,
    }

    def match(
            self,
            cv: CV,
            job: JobOffer,
    ) -> MatchResult:

        cv_technical_terms = (
                cv.skills
                + cv.tools
        )

        skills_score, matched_skills, missing_skills = (
            self._match_terms(
                cv_technical_terms,
                job.skills,
            )
        )

        tools_score, matched_tools, missing_tools = (
            self._match_terms(
                cv.tools,
                job.tools,
            )
        )

        languages_score, matched_languages, missing_languages = (
            self._match_terms(
                cv.languages,
                job.languages,
            )
        )

        # MVP : on garde ces deux scores simples
        # pour l'instant.
        experience_score = self._score_experience(
            cv,
            job.experience_required,
        )

        education_score = self._score_education(
            cv,
            job.education_required,
        )

        total_score = (
            skills_score * self.WEIGHTS["skills"]
            + tools_score * self.WEIGHTS["tools"]
            + languages_score * self.WEIGHTS["languages"]
            + experience_score * self.WEIGHTS["experience"]
            + education_score * self.WEIGHTS["education"]
        )

        return MatchResult(
            score=round(
                total_score * 100,
                2,
            ),
            details=MatchDetails(
                skills=round(
                    skills_score * 100,
                    2,
                ),
                tools=round(
                    tools_score * 100,
                    2,
                ),
                languages=round(
                    languages_score * 100,
                    2,
                ),
                experience=round(
                    experience_score * 100,
                    2,
                ),
                education=round(
                    education_score * 100,
                    2,
                ),
            ),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matched_tools=matched_tools,
            missing_tools=missing_tools,
            matched_languages=matched_languages,
            missing_languages=missing_languages,
        )

    @staticmethod
    def _match_terms(
        cv_terms: list[str],
        job_terms: list[str],
    ) -> tuple[float, list[str], list[str]]:

        normalized_cv = set(
            SkillNormalizer.normalize_many(
                cv_terms
            )
        )

        normalized_job = set(
            SkillNormalizer.normalize_many(
                job_terms
            )
        )

        if not normalized_job:
            return 1.0, [], []

        matched = sorted(
            normalized_cv
            & normalized_job
        )

        missing = sorted(
            normalized_job
            - normalized_cv
        )

        score = (
            len(matched)
            / len(normalized_job)
        )

        return score, matched, missing

    @staticmethod
    def _extract_required_experience(
            value: str | None,
    ) -> int | None:

        if not value:
            return None

        match = re.search(
            r"\b(\d+)\b",
            value,
        )

        if not match:
            return None

        return int(match.group(1))

    @staticmethod
    def _calculate_cv_experience_years(
            cv: CV,
    ) -> float:

        total_months = 0

        current_year = datetime.now().year

        for experience in cv.experiences:

            if not experience.start_date:
                continue

            start_match = re.search(
                r"(19|20)\d{2}",
                experience.start_date,
            )

            if not start_match:
                continue

            start_year = int(
                start_match.group()
            )

            if experience.end_date:
                end_match = re.search(
                    r"(19|20)\d{2}",
                    experience.end_date,
                )
            else:
                end_match = None

            if end_match:
                end_year = int(
                    end_match.group()
                )
            else:
                end_year = current_year

            if end_year >= start_year:
                total_months += (
                                        end_year - start_year
                                ) * 12

        return total_months / 12

    @classmethod
    def _score_experience(
            cls,
            cv: CV,
            requirement: str | None,
    ) -> float:

        required_years = (
            cls._extract_required_experience(
                requirement
            )
        )

        if required_years is None:
            return 1.0

        if required_years <= 0:
            return 1.0

        cv_years = (
            cls._calculate_cv_experience_years(
                cv
            )
        )

        return min(
            cv_years / required_years,
            1.0,
        )

    @classmethod
    def _extract_education_level(
            cls,
            value: str | None,
    ) -> int | None:

        if not value:
            return None

        normalized = (
            value.strip()
            .lower()
        )

        for label, level in cls.EDUCATION_LEVELS.items():
            if label in normalized:
                return level

        return None

    @classmethod
    def _get_cv_education_level(
            cls,
            cv: CV,
    ) -> int | None:

        levels = []

        for education in cv.education:

            text = " ".join(
                part
                for part in (
                    education.degree,
                    education.institution,
                )
                if part
            )

            level = cls._extract_education_level(
                text
            )

            if level is not None:
                levels.append(level)

        if not levels:
            return None

        return max(levels)

    @classmethod
    def _score_education(
            cls,
            cv: CV,
            requirement: str | None,
    ) -> float:

        required_level = (
            cls._extract_education_level(
                requirement
            )
        )

        if required_level is None:
            return 1.0

        cv_level = cls._get_cv_education_level(
            cv
        )

        if cv_level is None:
            return 0.0

        return min(
            cv_level / required_level,
            1.0,
        )