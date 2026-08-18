from app.models.job import JobOffer
from app.models.match import (
    MatchExplanation,
    MatchResult,
)


class MatchExplanationService:

    def explain(
        self,
        job: JobOffer,
        match: MatchResult,
    ) -> MatchExplanation:

        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        # -----------------------------------------------------
        # Skills
        # -----------------------------------------------------

        if job.skills:

            if match.details.skills >= 80:
                strengths.append(
                    "Très bonne couverture des compétences "
                    "techniques demandées."
                )

            elif match.details.skills < 50:
                weaknesses.append(
                    "Plusieurs compétences techniques "
                    "demandées sont absentes du CV."
                )

            if match.missing_skills:
                missing = ", ".join(
                    match.missing_skills
                )

                recommendations.append(
                    "Mettre en avant une expérience avec "
                    f"les compétences suivantes si elles "
                    f"sont maîtrisées : {missing}."
                )

        # -----------------------------------------------------
        # Tools
        # -----------------------------------------------------

        if job.tools:

            if match.details.tools >= 80:
                strengths.append(
                    "Très bonne maîtrise apparente des "
                    "outils et technologies demandés."
                )

            elif match.details.tools < 50:
                weaknesses.append(
                    "La couverture des outils demandés "
                    "est insuffisante."
                )

            if match.missing_tools:
                missing = ", ".join(
                    match.missing_tools
                )

                weaknesses.append(
                    "Outils ou technologies manquants : "
                    f"{missing}."
                )

                recommendations.append(
                    "Ajouter au CV des projets ou "
                    "expériences utilisant "
                    f"{missing}, uniquement si ces "
                    "technologies sont réellement maîtrisées."
                )

        # -----------------------------------------------------
        # Experience
        # -----------------------------------------------------

        if job.experience_required:

            if match.details.experience >= 100:
                strengths.append(
                    "Le niveau d'expérience demandé "
                    "est atteint."
                )

            elif match.details.experience < 100:
                weaknesses.append(
                    "L'expérience pertinente identifiée "
                    "dans le CV est inférieure au niveau "
                    f"demandé ({job.experience_required})."
                )

                recommendations.append(
                    "Mieux détailler dans le CV les "
                    "expériences directement liées aux "
                    "compétences de cette offre."
                )

        # -----------------------------------------------------
        # Education
        # -----------------------------------------------------

        if job.education_required:

            if match.details.education >= 100:
                strengths.append(
                    "Le niveau de formation demandé "
                    "est atteint."
                )

            elif match.details.education < 100:
                weaknesses.append(
                    "Le niveau de formation détecté ne "
                    "correspond pas totalement au niveau "
                    f"demandé ({job.education_required})."
                )

        # -----------------------------------------------------
        # Languages
        # -----------------------------------------------------

        if job.languages:

            if match.details.languages >= 100:
                strengths.append(
                    "Les exigences linguistiques "
                    "sont couvertes."
                )

            elif match.missing_languages:
                missing = ", ".join(
                    match.missing_languages
                )

                weaknesses.append(
                    "Langues demandées non détectées : "
                    f"{missing}."
                )

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        summary = self._build_summary(
            match.score
        )

        return MatchExplanation(
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

    @staticmethod
    def _build_summary(
        score: float,
    ) -> str:

        if score >= 85:
            return (
                "Très forte compatibilité avec l'offre."
            )

        if score >= 70:
            return (
                "Bonne compatibilité avec l'offre, "
                "avec quelques points à renforcer."
            )

        if score >= 50:
            return (
                "Compatibilité moyenne avec l'offre."
            )

        return (
            "Compatibilité limitée avec l'offre."
        )