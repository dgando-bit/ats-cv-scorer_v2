import re

from app.models.job import JobOffer


class JobRelevanceScorer:
    """
    Mesure la pertinence d'une offre par rapport
    aux mots-clés de recherche.

    Ce score est distinct du matching CV ↔ offre.
    """

    def score(
        self,
        job: JobOffer,
        keywords: str,
    ) -> float:
        query = self._normalize(keywords)

        if not query:
            return 0.0

        title = self._normalize(job.title or "")
        description = self._normalize(
            job.description or ""
        )

        # Le titre est le signal le plus important.
        title_score = self._text_score(
            query,
            title,
        )

        # La description permet de distinguer une
        # vraie offre ML d'une simple mention du ML.
        description_score = self._text_score(
            query,
            description,
        )

        score = (
            title_score * 0.7
            + description_score * 0.3
        )

        return round(score, 2)

    @staticmethod
    def _normalize(value: str) -> str:
        value = value.lower().strip()

        value = re.sub(
            r"[^a-z0-9+#.\-\s]",
            " ",
            value,
        )

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    def _text_score(
        self,
        query: str,
        text: str,
    ) -> float:
        if not text:
            return 0.0

        # Expression complète :
        # "machine learning" dans le texte.
        if query in text:
            return 100.0

        query_terms = {
            term
            for term in query.split()
            if len(term) >= 2
        }

        if not query_terms:
            return 0.0

        text_terms = set(text.split())

        matched = (
            query_terms
            & text_terms
        )

        return (
            len(matched)
            / len(query_terms)
            * 100.0
        )