# import re
#
#
# class SectionDetector:
#     """Detect CV sections based on their headings."""
#
#     SECTION_PATTERNS = {
#         "profile": [
#             r"^profil$",
#             r"^à propos$",
#             r"^résumé$",
#             r"^about$",
#         ],
#         "experience": [
#             r"^expériences?$",
#             r"^expérience professionnelle$",
#             r"^expériences professionnelles$",
#             r"^professional experience$",
#             r"^work experience$",
#         ],
#         "education": [
#             r"^formation$",
#             r"^formations$",
#             r"^education$",
#             r"^academic background$",
#         ],
#         "skills": [
#             r"^compétences$",
#             r"^compétences clés$",
#             r"^skills$",
#             r"^technical skills$",
#         ],
#         "languages": [
#             r"^langues?$",
#             r"^languages?$",
#         ],
#         "contact": [
#             r"^contact$",
#             r"^coordonnées$",
#         ],
#         "projects": [
#             r"^projets?$",
#             r"^projets académiques?$",
#             r"^academic projects?$",
#         ],
#         "certifications": [
#             r"^certifications?$",
#             r"^certificats?$",
#         ],
#     }
#
#     def detect(self, text: str) -> dict[str, str]:
#         sections = {}
#         current_section = None
#         current_lines = []
#
#         for line in text.splitlines():
#             line = line.strip()
#
#             if not line:
#                 continue
#
#             section = self._match_section(line)
#
#             if section:
#                 if current_section:
#                     sections[current_section] = "\n".join(
#                         current_lines
#                     ).strip()
#
#                 current_section = section
#                 current_lines = []
#                 continue
#
#             if current_section:
#                 current_lines.append(line)
#
#         if current_section:
#             sections[current_section] = "\n".join(
#                 current_lines
#             ).strip()
#
#         return sections
#
#     def _match_section(self, line: str) -> str | None:
#         normalized = self._normalize(line)
#
#         for section, patterns in self.SECTION_PATTERNS.items():
#             for pattern in patterns:
#                 if re.fullmatch(pattern, normalized, re.IGNORECASE):
#                     return section
#
#         return None
#
#     @staticmethod
#     def _normalize(text: str) -> str:
#         text = text.strip()
#         text = re.sub(r"\s+", " ", text)
#
#         return text

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

        sections: list[DetectedSection] = []

        current_section = None
        current_blocks: list[TextBlock] = []

        for block in blocks:

            section_name = self._match_section(block.text)

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

    def _match_section(self, text: str) -> str | None:

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