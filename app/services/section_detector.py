from dataclasses import dataclass

from app.services.layout_extractor import TextBlock


@dataclass
class DetectedSection:
    name: str
    blocks: list[TextBlock]


class SectionDetector:

    SECTION_ALIASES = {
        "profile": {
            "profil",
            "profile",
            "summary",
            "professional summary",
            "about me",
            "à propos",
        },
        "experience": {
            "expériences",
            "experiences",
            "experience",
            "work experience",
            "professional experience",
        },
        "skills": {
            "compétences",
            "competences",
            "compétences clés",
            "skills",
            "technical skills",
            "core skills",
        },
        "education": {
            "formation",
            "formations",
            "education",
            "academic background",
        },
        "languages": {
            "langues",
            "languages",
        },
        "contact": {
            "contact",
            "coordonnées",
            "contact information",
        },
        "soft_skills": {
            "soft-skills",
            "soft skills",
            "qualités",
            "personal skills",
        },
        "tools": {
            "outils",
            "tools",
            "technologies",
        },
    }

    def detect(
        self,
        blocks: list[TextBlock],
    ) -> list[DetectedSection]:

        if not blocks:
            return []

        # Pour l'instant, on traite chaque colonne séparément.
        columns = self._split_columns(blocks)

        sections: list[DetectedSection] = []

        for column_blocks in columns:

            column_sections = self._detect_column(
                column_blocks
            )

            sections.extend(column_sections)

        return sections

    def _detect_column(
        self,
        blocks: list[TextBlock],
    ) -> list[DetectedSection]:

        sections: list[DetectedSection] = []

        current_section: str | None = None
        current_blocks: list[TextBlock] = []

        # Lecture verticale dans la colonne
        blocks = sorted(
            blocks,
            key=lambda block: block.y0,
        )

        for block in blocks:

            section_name = self._match_section(
                block.text
            )

            if section_name:

                if current_section is not None:
                    sections.append(
                        DetectedSection(
                            name=current_section,
                            blocks=current_blocks,
                        )
                    )

                current_section = section_name
                current_blocks = []

                continue

            if current_section is not None:
                current_blocks.append(block)

        if current_section is not None:
            sections.append(
                DetectedSection(
                    name=current_section,
                    blocks=current_blocks,
                )
            )

        return sections

    @staticmethod
    def _split_columns(
        blocks: list[TextBlock],
    ) -> list[list[TextBlock]]:

        left_column = []
        right_column = []

        for block in blocks:

            # Ton PDF utilise environ x=220 comme séparation.
            if block.x0 < 180:
                left_column.append(block)
            else:
                right_column.append(block)

        return [
            left_column,
            right_column,
        ]

    def _match_section(
        self,
        text: str,
    ) -> str | None:

        normalized = self._normalize(text)

        for section_name, aliases in self.SECTION_ALIASES.items():

            if normalized in aliases:
                return section_name

        return None

    @staticmethod
    def _normalize(text: str) -> str:

        return (
            text.strip()
            .lower()
            .replace(":", "")
        )