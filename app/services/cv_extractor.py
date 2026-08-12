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

        # 9. Skills
        skills_text = self._blocks_to_text(
            sections.get("skills", [])
        )

        skills = self._extract_skills(
            skills_text
        )

        # 10. Languages
        languages_text = self._blocks_to_text(
            sections.get("languages", [])
        )

        languages = self._extract_languages(
            languages_text
        )

        return CV(
            candidate_name=candidate_name,
            title=title,
            contact=contact,
            profile=profile,
            experiences=experiences,
            education=education,
            skills=skills,
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

    @staticmethod
    def _extract_candidate_name(blocks):

        if not blocks:
            return None

        return blocks[0].text.strip()

    @staticmethod
    def _extract_title(blocks):

        if len(blocks) < 2:
            return None

        return blocks[1].text.strip()

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

    @staticmethod
    def _extract_skills(text: str) -> list[str]:

        if not text:
            return []

        return [
            skill.strip()
            for skill in text.splitlines()
            if skill.strip()
        ]

    @staticmethod
    def _extract_languages(text: str) -> list[str]:

        if not text:
            return []

        return [
            language.strip()
            for language in text.splitlines()
            if language.strip()
        ]