from app.services.layout_extractor import LayoutExtractor
from app.services.section_detector import SectionDetector
from app.services.experience_extractor import ExperienceExtractor


PDF_PATH = "data/samples/cv_test.pdf"


layout_extractor = LayoutExtractor()
section_detector = SectionDetector()
experience_extractor = ExperienceExtractor()

blocks = layout_extractor.extract(PDF_PATH)

sections = section_detector.detect(blocks)

experience_sections = [
    section
    for section in sections
    if section.name == "experience"
]

print("=" * 80)
print("SECTIONS EXPERIENCE")
print("=" * 80)

for section in experience_sections:
    print()
    print(f"Nombre de blocs : {len(section.blocks)}")

    for block in section.blocks:
        print(
            f"y={block.y0:6.1f} "
            f"x={block.x0:6.1f} "
            f"| {block.text!r}"
        )

    experiences = experience_extractor.extract(
        section.blocks
    )

    print()
    print("=" * 80)
    print("EXPERIENCES EXTRAITEES")
    print("=" * 80)

    for index, experience in enumerate(experiences, start=1):
        print()
        print(f"### EXPERIENCE {index}")
        print(f"Company    : {experience.company}")
        print(f"Role       : {experience.role}")
        print(f"Start date : {experience.start_date}")
        print(f"End date   : {experience.end_date}")

        print("Description:")

        for line in experience.description:
            print(f"  - {line}")