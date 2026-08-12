import re

from app.models.cv import Education
from app.services.layout_extractor import TextBlock


class EducationExtractor:

    YEAR_RANGE_PATTERN = re.compile(
        r"\b((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2})\b"
    )

    YEAR_PATTERN = re.compile(
        r"\b((?:19|20)\d{2})\b"
    )

    def extract(
        self,
        blocks: list[TextBlock],
    ) -> list[Education]:

        if not blocks:
            return []

        # La section Formation de notre CV est organisée
        # en paires : diplôme puis établissement.
        lines = [
            block.text.strip()
            for block in blocks
            if block.text.strip()
        ]

        educations: list[Education] = []

        i = 0

        while i < len(lines):

            degree_line = lines[i]

            year = self._extract_year(degree_line)

            degree = self._remove_year(
                degree_line
            )

            institution = None

            if i + 1 < len(lines):
                institution = lines[i + 1].strip()

            educations.append(
                Education(
                    institution=institution,
                    degree=degree,
                    year=year,
                )
            )

            i += 2

        return educations

    def _extract_year(
        self,
        text: str,
    ) -> str | None:

        range_match = self.YEAR_RANGE_PATTERN.search(text)

        if range_match:
            return (
                f"{range_match.group(1)}-"
                f"{range_match.group(2)}"
            )

        year_match = self.YEAR_PATTERN.search(text)

        if year_match:
            return year_match.group(1)

        return None

    def _remove_year(
        self,
        text: str,
    ) -> str:

        text = self.YEAR_RANGE_PATTERN.sub(
            "",
            text,
        )

        text = self.YEAR_PATTERN.sub(
            "",
            text,
        )

        return (
            text
            .replace(":", " ")
            .strip()
        )