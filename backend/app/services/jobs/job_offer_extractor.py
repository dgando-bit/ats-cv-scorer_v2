import re

from app.models.job import JobOffer


class JobOfferExtractor:

    SKILLS = {
        "python",
        "sql",
        "machine learning",
        "deep learning",
        "nlp",
        "computer vision",
        "data science",
        "data engineering",
        "rag",
        "llm",
    }

    TOOLS = {
        "docker",
        "kubernetes",
        "airflow",
        "mlflow",
        "git",
        "pandas",
        "numpy",
        "scikit-learn",
        "sklearn",
        "pytorch",
        "tensorflow",
        "spark",
        "fastapi",
        "postgresql",
        "aws",
        "gcp",
        "azure",
    }

    LANGUAGE_PATTERN = re.compile(
        r"\b("
        r"anglais|english|"
        r"français|french|"
        r"allemand|german|"
        r"espagnol|spanish"
        r")\b",
        re.IGNORECASE,
    )

    EXPERIENCE_PATTERN = re.compile(
        r"\b(\d+)\s*(?:ans?|années?|years?)"
        r"(?:\s+d['’]expérience)?\b",
        re.IGNORECASE,
    )

    EDUCATION_PATTERN = re.compile(
        r"\b("
        r"bac\s*\+\s*[2-8]"
        r"|master(?:'s)?"
        r"|bachelor"
        r"|doctorat"
        r"|phd"
        r")\b",
        re.IGNORECASE,
    )

    def extract(
        self,
        text: str,
        *,
        title: str | None = None,
        company: str | None = None,
        location: str | None = None,
        contract_type: str | None = None,
        job_id: str | None = None,
        source: str | None = None,
        source_url: str | None = None,
    ) -> JobOffer:

        normalized = text.lower()

        skills = self._extract_terms(
            normalized,
            self.SKILLS,
        )

        tools = self._extract_terms(
            normalized,
            self.TOOLS,
        )

        experience_required = (
            self._extract_experience(text)
        )

        education_required = (
            self._extract_education(text)
        )

        languages = self._extract_languages(
            text
        )

        return JobOffer(
            id=job_id,
            title=title or "",
            company=company,
            location=location,
            contract_type=contract_type,
            description=text,
            skills=skills,
            tools=tools,
            languages=languages,
            experience_required=experience_required,
            education_required=education_required,
            source=source,
            source_url=source_url,
        )

    @staticmethod
    def _extract_terms(
        normalized_text: str,
        terms: set[str],
    ) -> list[str]:

        found = []

        for term in terms:

            if re.search(
                rf"\b{re.escape(term)}\b",
                normalized_text,
                flags=re.IGNORECASE,
            ):
                found.append(term)

        return sorted(found)

    @classmethod
    def _extract_experience(
        cls,
        text: str,
    ) -> str | None:

        match = cls.EXPERIENCE_PATTERN.search(
            text
        )

        if not match:
            return None

        return f"{match.group(1)} ans"

    @classmethod
    def _extract_education(
        cls,
        text: str,
    ) -> str | None:

        match = cls.EDUCATION_PATTERN.search(
            text
        )

        if not match:
            return None

        return match.group(1)

    @classmethod
    def _extract_languages(
        cls,
        text: str,
    ) -> list[str]:

        matches = cls.LANGUAGE_PATTERN.findall(
            text
        )

        return list(
            dict.fromkeys(
                match.capitalize()
                for match in matches
            )
        )