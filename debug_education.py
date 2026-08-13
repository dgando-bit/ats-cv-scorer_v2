from app.services.layout_extractor import LayoutExtractor
from app.services.section_detector import SectionDetector


PDF_PATH = "data/samples/cv_test_1.pdf"

blocks = LayoutExtractor().extract(PDF_PATH)

sections = SectionDetector().detect(blocks)

for section in sections:
    if section.name != "education":
        continue

    print("=" * 80)
    print("SECTION EDUCATION")
    print("=" * 80)

    for block in section.blocks:
        print(
            f"y={block.y0:6.1f} "
            f"x={block.x0:6.1f} "
            f"| {block.text!r}"
        )