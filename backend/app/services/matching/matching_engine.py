import re
from datetime import datetime

from app.models.cv import CV
from app.models.job import JobOffer
from app.models.match import MatchDetails, MatchResult
from app.services.matching.skill_normalizer import SkillNormalizer
from app.services.matching.candidate_knowledge_extractor import (
    CandidateKnowledgeExtractor,
)
from app.services.matching.relevant_experience_calculator import (
    RelevantExperienceCalculator,
)

class MatchingEngine:

    WEIGHTS = {
        "skills": 0.40,
        "tools": 0.25,
        "languages": 0.10,
        "experience": 0.15,
        "education": 0.10,
    }

    EDUCATION_LEVELS = {
        "bts": 5,
        "bac+2": 5,
        "bac +2": 5,

        "bachelor": 6,
        "licence": 6,
        "bac+3": 6,
        "bac +3": 6,
        "niveau 6": 6,

        "master": 7,
        "bac+5": 7,
        "bac +5": 7,
        "niveau 7": 7,

        "doctorat": 8,
        "phd": 8,
        "bac+8": 8,
        "bac +8": 8,
        "niveau 8": 8,
    }

    def __init__(self):
        self.candidate_knowledge_extractor = (
            CandidateKnowledgeExtractor()
        )

        self.relevant_experience_calculator = (
            RelevantExperienceCalculator()
        )

    def match(
        self,
        cv: CV,
        job: JobOffer,
    ) -> MatchResult:

        # ---------------------------------------------------------
        # 1. Compétences techniques
        #
        # Une compétence demandée dans l'offre peut se trouver
        # dans cv.skills ou cv.tools.
        # ---------------------------------------------------------

        candidate_knowledge = (
            self.candidate_knowledge_extractor.extract(cv)
        )

        cv_technical_terms = candidate_knowledge.terms

        (
            skills_score,
            matched_skills,
            missing_skills,
        ) = self._match_terms(
            cv_technical_terms,
            job.skills,
        )

        # ---------------------------------------------------------
        # 2. Outils / technologies
        # ---------------------------------------------------------

        (
            tools_score,
            matched_tools,
            missing_tools,
        ) = self._match_terms(
            cv_technical_terms,
            job.tools,
        )

        # ---------------------------------------------------------
        # 3. Langues
        # ---------------------------------------------------------

        (
            languages_score,
            matched_languages,
            missing_languages,
        ) = self._match_terms(
            cv.languages,
            job.languages,
        )

        # ---------------------------------------------------------
        # 4. Expérience
        # ---------------------------------------------------------

        experience_score = self._score_experience(
            cv=cv,
            requirement=job.experience_required,
            required_terms=(
                    job.skills
                    + job.tools
            ),
        )

        # ---------------------------------------------------------
        # 5. Formation
        # ---------------------------------------------------------

        education_score = self._score_education(
            cv,
            job.education_required,
        )

        # ---------------------------------------------------------
        # 6. Catégories applicables
        #
        # Une catégorie non demandée par l'offre est considérée N/A.
        # Elle apparaît à 0 dans les détails mais n'entre pas dans
        # le calcul du score global.
        # ---------------------------------------------------------

        scores = {
            "skills": skills_score,
            "tools": tools_score,
            "languages": languages_score,
            "experience": experience_score,
            "education": education_score,
        }

        applicable = {
            "skills": bool(job.skills),
            "tools": bool(job.tools),
            "languages": bool(job.languages),
            "experience": bool(
                job.experience_required
            ),
            "education": bool(
                job.education_required
            ),
        }

        weighted_score = 0.0
        applicable_weight = 0.0

        for category, score in scores.items():

            if not applicable[category]:
                continue

            weight = self.WEIGHTS[category]

            weighted_score += (
                score * weight
            )

            applicable_weight += weight

        if applicable_weight > 0:
            total_score = (
                weighted_score
                / applicable_weight
            )
        else:
            total_score = 0.0

        # ---------------------------------------------------------
        # 7. Résultat structuré
        # ---------------------------------------------------------

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
    ) -> tuple[
        float,
        list[str],
        list[str],
    ]:

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

        # Aucun critère demandé :
        # catégorie non applicable.
        if not normalized_job:
            return 0.0, [], []

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

        return (
            score,
            matched,
            missing,
        )

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

        return int(
            match.group(1)
        )

    @staticmethod
    def _calculate_cv_experience_years(
        cv: CV,
    ) -> float:

        total_months = 0

        current_year = (
            datetime.now().year
        )

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
                    end_year
                    - start_year
                ) * 12

        return total_months / 12

    def _score_experience(
            self,
            cv: CV,
            requirement: str | None,
            required_terms: list[str],
    ) -> float:

        required_years = (
            self._extract_required_experience(
                requirement
            )
        )

        if required_years is None:
            return 0.0

        if required_years <= 0:
            return 0.0

        # Si l'offre fournit des compétences ou technologies,
        # on mesure l'expérience pertinente par rapport à celles-ci.
        if required_terms:

            experience_years = (
                self.relevant_experience_calculator.calculate(
                    cv=cv,
                    required_terms=required_terms,
                )
            )

        # Si l'offre indique seulement un nombre d'années sans
        # préciser de domaine, on utilise l'expérience totale.
        else:

            experience_years = (
                self._calculate_cv_experience_years(
                    cv
                )
            )

        return min(
            experience_years / required_years,
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

        for (
            label,
            level,
        ) in cls.EDUCATION_LEVELS.items():

            if label in normalized:
                return level

        return None

    @classmethod
    def _get_cv_education_level(
            cls,
            cv: CV,
    ) -> int | None:

        levels: list[int] = []

        for education in cv.education:

            text = " ".join(
                part
                for part in (
                    education.degree,
                    education.level,
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
            return 0.0

        cv_level = (
            cls._get_cv_education_level(
                cv
            )
        )

        if cv_level is None:
            return 0.0

        if cv_level >= required_level:
            return 1.0

        gap = required_level - cv_level

        if gap == 1:
            return 0.70

        if gap == 2:
            return 0.40

        return 0.20