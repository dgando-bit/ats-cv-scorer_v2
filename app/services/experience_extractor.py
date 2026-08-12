import re

from app.models.cv import Experience
from app.services.layout_extractor import TextBlock


class ExperienceExtractor:

    DATE_RANGE_PATTERN = re.compile(
        r"\(?\s*(\d{4})\s*[-–]\s*(\d{4}|présent|present|aujourd'hui)\s*\)?",
        re.IGNORECASE,
    )

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

    @staticmethod
    def _extract_role_company(
            header: str,
    ) -> tuple[str | None, str | None]:

        header = header.strip()

        known_roles = [
            "IA & Machine Learning Engineer",
            "Développeur Back-end",
            "Développeur Informatique",
            "Responsable Informatique",
        ]

        header_lower = header.lower()

        for role in known_roles:
            role_lower = role.lower()

            if role_lower in header_lower:
                index = header_lower.find(role_lower)

                company_before = header[:index].strip()
                company_after = header[index + len(role):].strip()

                company_parts = [
                    part
                    for part in [company_before, company_after]
                    if part
                ]

                company = " ".join(company_parts)

                return role, company

        return None, header