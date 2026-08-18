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
            self._extract_experience_requirement(text)
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

    @staticmethod
    def _extract_experience_requirement(
            text: str,
    ) -> str | None:

        patterns = [
            # "2+ ans d'expérience"
            r"\b(\d+)\s*\+\s*ans?\s+d['’]expérience\b",

            # "minimum 5 ans d'expérience"
            # "au moins 3 ans d'expérience"
            r"\b(?:minimum|au\s+moins)\s+(\d+)\s+ans?"
            r"\s+d['’]expérience\b",

            # "5 ans d'expérience"
            r"\b(\d+)\s+ans?\s+d['’]expérience\b",

            # "4 années d'expérience"
            r"\b(\d+)\s+années?\s+d['’]expérience\b",

            # "expérience de 3 ans"
            r"\bexpérience\s+(?:professionnelle\s+)?de\s+"
            r"(\d+)\s+ans?\b",

            # "Expérience professionnelle : 5 ans"
            r"\bexpérience\s+professionnelle\s*:\s*"
            r"(\d+)\s+ans?\b",
        ]

        for index, pattern in enumerate(patterns):

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            years = match.group(1)

            # On conserve le "+" pour une exigence du type "2+ ans".
            if index == 0:
                return f"{years}+ ans"

            return f"{years} ans"

        return None