import re

from app.models.cv import CV, Contact
from app.services.document_parser import DocumentParser
from app.services.layout_extractor import LayoutExtractor
from app.services.section_detector import SectionDetector
from app.services.experience_extractor import ExperienceExtractor
from app.services.regex_extractor import RegexExtractor
from app.services.education_extractor import EducationExtractor

class CVExtractor:

    def __init__(self):
        self.document_parser = DocumentParser()
        self.layout_extractor = LayoutExtractor()
        self.section_detector = SectionDetector()
        self.experience_extractor = ExperienceExtractor()
        self.regex_extractor = RegexExtractor()
        self.education_extractor = EducationExtractor()

    def extract(self, file_path: str) -> CV:

        # 1. Extract raw document
        document = self.document_parser.parse(file_path)

        # 2. Extract layout blocks
        blocks = self.layout_extractor.extract(file_path)

        # 3. Detect CV sections
        detected_sections = self.section_detector.detect(blocks)

        # Convert detected sections to dictionary
        sections = self._sections_to_dict(
            detected_sections
        )

        # 4. Candidate information
        candidate_name = self._extract_candidate_name(blocks)
        title = self._extract_title(blocks)

        # 5. Contact
        contact_text = self._blocks_to_text(
            sections.get("contact", [])
        )

        contact = self._extract_contact(
            contact_text
        )

        # 6. Profile
        profile = self._blocks_to_text(
            sections.get("profile", [])
        )

        # 7. Experiences
        experience_blocks = sections.get(
            "experience",
            []
        )

        experiences = self.experience_extractor.extract(
            experience_blocks
        )

        # 8. Education
        education_blocks = sections.get(
            "education",
            []
        )

        education = self.education_extractor.extract(
            education_blocks
        )

        # 9. Skills / soft skills / tools
        skills = self._extract_list_section(
            sections, "skills"
        )

        soft_skills = self._extract_list_section(
            sections, "soft_skills"
        )

        tools = self._extract_list_section(
            sections, "tools"
        )

        # 10. Languages
        languages = self._extract_list_section(
            sections, "languages"
        )

        return CV(
            candidate_name=candidate_name,
            title=title,
            contact=contact,
            profile=profile,
            experiences=experiences,
            education=education,
            skills=skills,
            soft_skills=soft_skills,
            tools=tools,
            languages=languages,
        )

    @staticmethod
    def _sections_to_dict(
        detected_sections,
    ):

        return {
            section.name: section.blocks
            for section in detected_sections
        }

    @staticmethod
    def _blocks_to_text(
        blocks,
    ) -> str:

        return "\n".join(
            block.text
            for block in blocks
        )

    @classmethod
    def _extract_candidate_name(
            cls,
            blocks,
    ) -> str | None:
        """Extract the candidate name from the top area of the CV."""

        if not blocks:
            return None

        candidates = [
            block
            for block in blocks
            if (
                    block.text.strip()
                    and not cls._looks_like_section_heading(
                block.text
            )
            )
        ]

        if not candidates:
            return None

        # Le nom se trouve généralement parmi les blocs
        # les plus hauts du document.
        candidates = sorted(
            candidates,
            key=lambda block: (
                block.page,
                block.y0,
            ),
        )

        return candidates[0].text.strip()

    @classmethod
    def _extract_title(
            cls,
            blocks,
    ) -> str | None:
        """Extract the professional title located below the candidate name."""

        if not blocks:
            return None

        name_block = cls._find_candidate_name_block(
            blocks
        )

        if name_block is None:
            return None

        candidates = []

        for block in blocks:

            text = block.text.strip()

            if not text:
                continue

            if block.page != name_block.page:
                continue

            if block.y0 <= name_block.y0:
                continue

            if cls._looks_like_section_heading(text):
                continue

            # Un titre professionnel est généralement court.
            if "\n" in text:
                continue

            if len(text) > 80:
                continue

            candidates.append(block)

        if not candidates:
            return None

        # Priorité :
        # 1. proximité verticale avec le nom
        # 2. proximité horizontale
        candidates = sorted(
            candidates,
            key=lambda block: (
                block.y0 - name_block.y0,
                abs(
                    block.center_x
                    - name_block.center_x
                ),
            ),
        )

        return candidates[0].text.strip()

    @classmethod
    def _find_candidate_name_block(
            cls,
            blocks,
    ):
        """Return the TextBlock most likely containing the candidate name."""

        candidates = [
            block
            for block in blocks
            if (
                    block.text.strip()
                    and not cls._looks_like_section_heading(
                block.text
            )
            )
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda block: (
                block.page,
                block.y0,
            ),
        )

    @staticmethod
    def _looks_like_section_heading(
            text: str,
    ) -> bool:
        """Return True if text is a known CV section heading."""

        normalized = (
            text.strip()
            .lower()
            .replace(":", "")
        )

        return any(
            normalized in aliases
            for aliases
            in SectionDetector.SECTION_ALIASES.values()
        )

    def _extract_contact(self, text: str) -> Contact:

        if not text:
            return Contact()

        extracted = self.regex_extractor.extract(text)

        emails = extracted.get("emails", [])
        phones = extracted.get("phones", [])

        return Contact(
            email=emails[0] if emails else None,
            phone=phones[0] if phones else None,
            location=self._extract_location(text),
        )

    @staticmethod
    def _extract_location(text: str) -> str | None:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for line in lines:

            # Une ligne qui n'est ni téléphone ni email
            # peut correspondre à une localisation.
            if "@" not in line and not any(
                    char.isdigit() for char in line
            ):
                return line

        return None

    # Séparateurs courants utilisés dans les CV pour lister des
    # éléments sur une même ligne : virgule, point-virgule, puces
    # (•, ·, ‣, -, *), barre verticale...
    _LIST_SEPARATOR_PATTERN = re.compile(
        r"[,;•·‣|]|(?<=\S)\s[-*]\s(?=\S)"
    )

    @classmethod
    def _extract_list_section(
        cls,
        sections: dict,
        section_name: str,
    ) -> list[str]:
        """Extract a section made of a simple list of items
        (skills, soft_skills, tools, languages...).
        """

        text = cls._blocks_to_text(
            sections.get(section_name, [])
        )

        return cls._split_list_items(text)

    @classmethod
    def _split_list_items(cls, text: str) -> list[str]:
        """Split a block of text into individual list items.

        Gère à la fois le cas où chaque élément est sur sa propre
        ligne et le cas où plusieurs éléments sont regroupés sur une
        même ligne, séparés par une virgule, un point-virgule ou une
        puce.
        """

        if not text:
            return []

        items: list[str] = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            parts = cls._LIST_SEPARATOR_PATTERN.split(line)

            for part in parts:
                part = part.strip(" \t-*•·‣")

                if part:
                    items.append(part)

        return items