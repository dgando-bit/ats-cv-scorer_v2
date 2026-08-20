import re

from app.models.cv import CV
from app.services.matching.language_normalizer import (
    LanguageNormalizer,
)


class CandidateLanguageResolver:
    """
    Résout les langues du candidat utilisables
    pour le matching.

    Les langues explicitement déclarées dans le CV
    restent prioritaires.

    Une langue peut être inférée sans niveau lorsque
    plusieurs indices du CV montrent clairement que
    le candidat utilise cette langue.

    Aucun niveau CECRL n'est inventé.
    """

    FRENCH_MARKERS = {
        "développeur",
        "développement",
        "informatique",
        "ingénieur",
        "ingénierie",
        "expérience",
        "expériences",
        "formation",
        "formations",
        "compétence",
        "compétences",
        "conception",
        "application",
        "applications",
        "université",
        "école",
        "responsable",
        "projet",
        "projets",
        "donnée",
        "données",
        "système",
        "systèmes",
        "analyse",
        "gestion",
    }

    MIN_FRENCH_MARKERS = 3

    def resolve(
        self,
        cv: CV,
    ) -> list[str]:
        languages = list(
            cv.languages
        )

        normalized_languages = {
            LanguageNormalizer.normalize(
                language
            ).language
            for language in languages
        }

        # Si le français est déjà déclaré,
        # on ne fait aucune inférence.
        if "français" in normalized_languages:
            return languages

        if self._has_strong_french_evidence(
            cv
        ):
            # On infère uniquement la langue.
            # Le niveau reste inconnu.
            languages.append(
                "Français"
            )

        return languages

    @classmethod
    def _has_strong_french_evidence(
        cls,
        cv: CV,
    ) -> bool:
        text = cls._build_candidate_text(
            cv
        )

        tokens = set(
            re.findall(
                r"[a-zà-ÿ]+",
                text.casefold(),
            )
        )

        matches = (
            tokens
            & cls.FRENCH_MARKERS
        )

        return (
            len(matches)
            >= cls.MIN_FRENCH_MARKERS
        )

    @staticmethod
    def _build_candidate_text(
        cv: CV,
    ) -> str:
        parts: list[str] = []

        if cv.title:
            parts.append(
                cv.title
            )

        if cv.profile:
            parts.append(
                cv.profile
            )

        for experience in cv.experiences:
            if experience.role:
                parts.append(
                    experience.role
                )

            if experience.company:
                parts.append(
                    experience.company
                )

            parts.extend(
                experience.description
            )

        for education in cv.education:
            if education.degree:
                parts.append(
                    education.degree
                )

            if education.institution:
                parts.append(
                    education.institution
                )

            if education.level:
                parts.append(
                    education.level
                )

        return " ".join(
            parts
        )