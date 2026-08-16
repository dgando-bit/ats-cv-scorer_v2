import sys

from app.services.experience_extractor import ExperienceExtractor
from app.services.layout_analyzer import LayoutAnalyzer
from app.services.layout_extractor import LayoutExtractor
from app.services.section_detector import SectionDetector


def main():

    if len(sys.argv) != 2:
        print(
            "Usage: "
            "uv run python scripts/run_experiences.py <cv_file>"
        )
        sys.exit(1)

    file_path = sys.argv[1]

    extractor = LayoutExtractor()
    blocks = extractor.extract(file_path)

    analyzer = LayoutAnalyzer()
    columns = analyzer.analyze(blocks)

    detector = SectionDetector()

    sections = detector.detect(
        columns["main"].blocks
    )

    experience_section = next(
        (
            section
            for section in sections
            if section.name == "experience"
        ),
        None,
    )

    if experience_section is None:
        print("No experience section found.")
        return

    experience_extractor = ExperienceExtractor()

    experiences = experience_extractor.extract(
        experience_section.blocks
    )

    print("=" * 80)
    print("EXPERIENCES")
    print("=" * 80)

    for experience in experiences:

        print("\n---")

        print(f"Company    : {experience.company}")
        print(f"Role       : {experience.role}")
        print(f"Start date : {experience.start_date}")
        print(f"End date   : {experience.end_date}")

        print("Description:")

        for item in experience.description:
            print(f"  - {item}")


if __name__ == "__main__":
    main()