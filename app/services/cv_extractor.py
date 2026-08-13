import re

from app.models.cv import CV, Contact
from app.services.document_parser import DocumentParser
from app.services.layout_extractor import LayoutExtractor, TextBlock
from app.services.section_detector import SectionDetector, DetectedSection
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


        # 1. Extract layout blocks
        blocks = self.layout_extractor.extract(file_path)

        # 2. Detect CV sections
        detected_sections = self.section_detector.detect(blocks)

        # Convert detected sections to dictionary
        sections = self._sections_to_dict(
            detected_sections
        )

        # 3. Candidate information
        candidate_name = self._extract_candidate_name(blocks)
        title = self._extract_title(blocks)

        # 4. Contact
        contact_text = self._blocks_to_text(
            sections.get("contact", [])
        )

        contact = self._extract_contact(
            contact_text
        )

        # 5. Profile
        profile = self._blocks_to_text(
            sections.get("profile", [])
        )

        # 6. Experiences
        experience_blocks = sections.get(
            "experience",
            []
        )

        experiences = self.experience_extractor.extract(
            experience_blocks
        )

        # 7. Education
        education_blocks = sections.get(
            "education",
            []
        )

        education = self.education_extractor.extract(
            education_blocks
        )

        # 8. Skills / soft skills / tools
        skills = self._extract_list_section(
            sections, "skills"
        )

        soft_skills = self._extract_list_section(
            sections, "soft_skills"
        )

        tools = self._extract_list_section(
            sections, "tools"
        )

        # 9. Languages
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
            detected_sections: list[DetectedSection],
    ) -> dict[str, list[TextBlock]]:

        return {
            section.name: section.blocks
            for section in detected_sections
        }

    @staticmethod
    def _blocks_to_text(
            blocks: list[TextBlock],
    ) -> str:

        return "\n".join(
            block.text
            for block in blocks
        )

    @classmethod
    def _extract_candidate_name(
            cls,
            blocks: list[TextBlock],
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
        urls = extracted.get("urls", [])

        return Contact(
            email=emails[0] if emails else None,
            phone=phones[0] if phones else None,
            location=self._extract_location(text),
            website=urls[0] if urls else None,
        )

    @staticmethod
    def _extract_location(text: str) -> str | None:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for line in lines:

            # Email
            if "@" in line:
                continue

            # URL / site web
            if (
                    line.lower().startswith("http://")
                    or line.lower().startswith("https://")
                    or line.lower().startswith("www.")
            ):
                continue

            # Téléphone / lignes numériques
            if any(char.isdigit() for char in line):
                continue

            return line

        return None

    @classmethod
    def _extract_list_section(
            cls,
            sections: dict,
            section_name: str,
    ) -> list[str]:
        """Extract a section made of a simple list of items."""

        text = cls._blocks_to_text(
            sections.get(section_name, [])
        )

        return cls._extract_list_items(text)

    @staticmethod
    def _extract_list_items(text: str) -> list[str]:
        """Extract list items while repairing wrapped lines."""

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return []

        reconstructed: list[str] = []
        current = ""

        for line in lines:
            if current:
                current += line
            else:
                current = line

            if current.count("(") > current.count(")"):
                continue

            reconstructed.append(current)
            current = ""

        if current:
            reconstructed.append(current)

        items: list[str] = []

        for item in reconstructed:
            parts = [
                part.strip()
                for part in re.split(
                    r"[,;•·‣|]",
                    item,
                )
                if part.strip()
            ]

            items.extend(parts)

        return items