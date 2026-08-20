import re
from datetime import datetime

from app.models.cv import CV
from app.models.job import JobOffer
from app.models.match import (
    MatchDetails,
    MatchResult,
)
from app.services.matching.skill_normalizer import (
    SkillNormalizer,
)
from app.services.matching.candidate_knowledge_extractor import (
    CandidateKnowledgeExtractor,
)
from app.services.matching.relevant_experience_calculator import (
    RelevantExperienceCalculator,
)
from app.services.matching.language_normalizer import (
    LanguageNormalizer,
)
from app.services.matching.candidate_language_resolver import (
    CandidateLanguageResolver,
)


class MatchingEngine:

    WEIGHTS = {
        "skills": 0.40,
        "tools": 0.20,
        "experience": 0.20,
        "education": 0.10,
        "languages": 0.10,
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

    def __init__(
        self,
    ) -> None:
        self.candidate_knowledge_extractor = (
            CandidateKnowledgeExtractor()
        )

        self.relevant_experience_calculator = (
            RelevantExperienceCalculator()
        )

        self.candidate_language_resolver = (
            CandidateLanguageResolver()
        )

    def match(
        self,
        cv: CV,
        job: JobOffer,
    ) -> MatchResult:

        # ---------------------------------------------------------
        # 1. Construire les connaissances techniques du candidat
        # ---------------------------------------------------------

        candidate_knowledge = (
            self.candidate_knowledge_extractor.extract(
                cv
            )
        )

        cv_technical_terms = (
            candidate_knowledge.terms
        )

        # ---------------------------------------------------------
        # 2. Compétences techniques
        # ---------------------------------------------------------

        (
            skills_score,
            matched_skills,
            missing_skills,
        ) = self._match_terms(
            cv_technical_terms,
            job.skills,
        )

        # ---------------------------------------------------------
        # 3. Outils / technologies
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
        # 4. Langues
        # ---------------------------------------------------------

        candidate_languages = (
            self.candidate_language_resolver.resolve(
                cv
            )
        )

        (
            languages_score,
            matched_languages,
            missing_languages,
        ) = self._match_languages(
            candidate_languages,
            job.languages,
        )

        # ---------------------------------------------------------
        # 5. Expérience
        # ---------------------------------------------------------

        experience_score = (
            self._score_experience(
                cv=cv,
                requirement=(
                    job.experience_required
                ),
                required_terms=(
                    job.skills
                    + job.tools
                ),
            )
        )

        # ---------------------------------------------------------
        # 6. Formation
        # ---------------------------------------------------------

        education_score = (
            self._score_education(
                cv,
                job.education_required,
            )
        )

        # ---------------------------------------------------------
        # 7. Convertir les sous-scores en pourcentages
        # ---------------------------------------------------------

        scores = {
            "skills": (
                skills_score
                * 100
            ),
            "tools": (
                tools_score
                * 100
            ),
            "languages": (
                languages_score
                * 100
            ),
            "experience": (
                experience_score
                * 100
            ),
            "education": (
                education_score
                * 100
            ),
        }

        # ---------------------------------------------------------
        # 8. Déterminer les catégories réellement applicables
        # ---------------------------------------------------------

        active = {
            "skills": bool(
                job.skills
            ),
            "tools": bool(
                job.tools
            ),
            "languages": bool(
                job.languages
            ),
            "experience": bool(
                job.experience_required
            ),
            "education": bool(
                job.education_required
            ),
        }

        # ---------------------------------------------------------
        # 9. Score global avec pondération dynamique
        # ---------------------------------------------------------

        total_score = (
            self._calculate_weighted_score(
                scores=scores,
                active=active,
            )
        )

        # ---------------------------------------------------------
        # 10. Résultat structuré
        # ---------------------------------------------------------

        return MatchResult(
            score=total_score,
            details=MatchDetails(
                skills=round(
                    scores["skills"],
                    2,
                ),
                tools=round(
                    scores["tools"],
                    2,
                ),
                languages=round(
                    scores["languages"],
                    2,
                ),
                experience=round(
                    scores["experience"],
                    2,
                ),
                education=round(
                    scores["education"],
                    2,
                ),
            ),
            matched_skills=(
                matched_skills
            ),
            missing_skills=(
                missing_skills
            ),
            matched_tools=(
                matched_tools
            ),
            missing_tools=(
                missing_tools
            ),
            matched_languages=(
                matched_languages
            ),
            missing_languages=(
                missing_languages
            ),
        )

    # =============================================================
    # Matching de termes
    # =============================================================

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

    # =============================================================
    # Expérience
    # =============================================================

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

        return (
            total_months
            / 12
        )

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
        # on calcule l'expérience pertinente.
        if required_terms:

            experience_years = (
                self.relevant_experience_calculator.calculate(
                    cv=cv,
                    required_terms=(
                        required_terms
                    ),
                )
            )

        # Sinon, on utilise l'expérience
        # professionnelle totale.
        else:

            experience_years = (
                self._calculate_cv_experience_years(
                    cv
                )
            )

        return min(
            experience_years
            / required_years,
            1.0,
        )

    # =============================================================
    # Formation
    # =============================================================

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

            level = (
                cls._extract_education_level(
                    text
                )
            )

            if level is not None:
                levels.append(
                    level
                )

        if not levels:
            return None

        return max(
            levels
        )

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

        # Niveau candidat suffisant
        # ou supérieur.
        if cv_level >= required_level:
            return 1.0

        gap = (
            required_level
            - cv_level
        )

        # Un niveau en dessous.
        if gap == 1:
            return 0.70

        # Deux niveaux en dessous.
        if gap == 2:
            return 0.40

        # Trois niveaux ou plus
        # en dessous.
        return 0.20

    # =============================================================
    # Score global pondéré
    # =============================================================

    @classmethod
    def _calculate_weighted_score(
        cls,
        scores: dict[str, float],
        active: dict[str, bool],
    ) -> float:

        weighted_sum = 0.0
        active_weight = 0.0

        for (
            category,
            weight,
        ) in cls.WEIGHTS.items():

            if not active.get(
                category,
                False,
            ):
                continue

            weighted_sum += (
                scores.get(
                    category,
                    0.0,
                )
                * weight
            )

            active_weight += weight

        if active_weight == 0:
            return 0.0

        return round(
            weighted_sum
            / active_weight,
            2,
        )

    # =============================================================
    # Langues
    # =============================================================

    @classmethod
    def _match_languages(
        cls,
        cv_languages: list[str],
        job_languages: list[str],
    ) -> tuple[
        float,
        list[str],
        list[str],
    ]:

        if not job_languages:
            return 0.0, [], []

        normalized_cv = [
            LanguageNormalizer.normalize(
                language
            )
            for language in cv_languages
        ]

        normalized_job = [
            LanguageNormalizer.normalize(
                language
            )
            for language in job_languages
        ]

        cv_by_language = {
            item.language: item
            for item in normalized_cv
        }

        matched: list[str] = []
        missing: list[str] = []

        total_score = 0.0

        for requirement in normalized_job:

            candidate = (
                cv_by_language.get(
                    requirement.language
                )
            )

            if candidate is None:
                missing.append(
                    requirement.language
                )
                continue

            requirement_level = (
                LanguageNormalizer.level_value(
                    requirement.level
                )
            )

            candidate_level = (
                LanguageNormalizer.level_value(
                    candidate.level
                )
            )

            # Aucun niveau demandé :
            # la langue suffit.
            if requirement_level is None:
                total_score += 1.0

                matched.append(
                    requirement.language
                )

                continue

            # Langue présente mais niveau
            # candidat inconnu.
            if candidate_level is None:
                total_score += 0.70

                matched.append(
                    requirement.language
                )

                continue

            # Niveau suffisant ou supérieur.
            if (
                candidate_level
                >= requirement_level
            ):
                total_score += 1.0

                matched.append(
                    requirement.language
                )

                continue

            # Niveau inférieur :
            # score proportionnel.
            total_score += (
                candidate_level
                / requirement_level
            )

            matched.append(
                requirement.language
            )

        score = (
            total_score
            / len(normalized_job)
        )

        return (
            score,
            sorted(
                set(matched)
            ),
            sorted(
                set(missing)
            ),
        )