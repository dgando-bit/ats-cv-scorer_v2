import re
from dataclasses import dataclass

from app.services.layout_extractor import TextBlock


@dataclass
class Experience:
    company: str | None
    role: str | None
    start_date: str | None
    end_date: str | None
    description: list[str]


class ExperienceExtractor:

    DATE_RANGE_PATTERN = re.compile(
        r"\(?\s*(\d{4})\s*[-–]\s*(\d{4}|présent|present|aujourd'hui)\s*\)?",
        re.IGNORECASE,
    )

    KNOWN_ROLES = [
        "IA & Machine Learning Engineer",
        "Développeur Back-end",
        "Développeur Informatique",
        "Responsable Informatique",
    ]

    def extract(
        self,
        blocks: list[TextBlock],
    ) -> list[Experience]:

        experiences = []
        current_blocks = []

        for block in blocks:

            if self._looks_like_experience_header(block.text):

                if current_blocks:
                    experiences.append(
                        self._build_experience(current_blocks)
                    )

                current_blocks = [block]

            else:
                if current_blocks:
                    current_blocks.append(block)

        if current_blocks:
            experiences.append(
                self._build_experience(current_blocks)
            )

        return experiences

    def _looks_like_experience_header(
        self,
        text: str,
    ) -> bool:

        return bool(
            self.DATE_RANGE_PATTERN.search(text)
        )

    def _build_experience(
        self,
        blocks: list[TextBlock],
    ) -> Experience:

        header = blocks[0].text

        date_match = self.DATE_RANGE_PATTERN.search(header)

        start_date = None
        end_date = None

        if date_match:
            start_date = date_match.group(1)
            end_date = date_match.group(2)

        header_without_date = (
            self.DATE_RANGE_PATTERN
            .sub("", header)
            .strip()
        )

        role, company = self._extract_role_company(
            header_without_date
        )

        description = [
            block.text
            for block in blocks[1:]
        ]

        return Experience(
            company=company,
            role=role,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

    @classmethod
    def _extract_role_company(
        cls,
        header: str,
    ) -> tuple[str | None, str | None]:

        header = header.strip()

        # ---------------------------------------------------------
        # Cas 1 :
        # "IA & Machine Learning Engineer Liora"
        # ---------------------------------------------------------
        for role in cls.KNOWN_ROLES:

            if header.startswith(role):

                company = header[len(role):].strip()

                return role, company

        # ---------------------------------------------------------
        # Cas 2 :
        # "Liora IA & Machine Learning Engineer"
        # ---------------------------------------------------------
        for role in cls.KNOWN_ROLES:

            if header.endswith(role):

                company = header[:-len(role)].strip()

                return role, company

        # ---------------------------------------------------------
        # Cas 3 :
        # Le rôle est au milieu du header
        #
        # "Liora - IA & Machine Learning Engineer"
        # ---------------------------------------------------------
        for role in cls.KNOWN_ROLES:

            if role in header:

                company = header.replace(role, "").strip()

                # Nettoyage des séparateurs éventuels
                company = company.strip(" -|,:;")

                return role, company

        # ---------------------------------------------------------
        # Aucun rôle reconnu
        # ---------------------------------------------------------
        return None, header