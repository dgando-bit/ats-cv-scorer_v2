# import sys
#
# from app.services.document_parser import DocumentParser
# from app.services.section_detector import SectionDetector
#
#
# def main():
#     if len(sys.argv) != 2:
#         print("Usage: uv run python scripts/run_sections.py <cv_file>")
#         sys.exit(1)
#
#     file_path = sys.argv[1]
#
#     text = DocumentParser.parse(file_path)
#
#     detector = SectionDetector()
#     sections = detector.detect(text)
#
#     print("=" * 80)
#     print("DETECTED SECTIONS")
#     print("=" * 80)
#
#     for name, content in sections.items():
#         print(f"\n[{name.upper()}]")
#         print("-" * 80)
#         print(content)
#
#     print("\n" + "=" * 80)
#
#
# if __name__ == "__main__":
#     main()

import sys

from app.services.layout_analyzer import LayoutAnalyzer
from app.services.layout_extractor import LayoutExtractor
from app.services.section_detector import SectionDetector


def main():

    if len(sys.argv) != 2:
        print(
            "Usage: "
            "uv run python scripts/run_sections.py <cv_file>"
        )
        sys.exit(1)

    file_path = sys.argv[1]

    extractor = LayoutExtractor()
    blocks = extractor.extract(file_path)

    analyzer = LayoutAnalyzer()
    columns = analyzer.analyze(blocks)

    detector = SectionDetector()

    for column_name, column in columns.items():

        print("\n" + "=" * 80)
        print(column_name.upper())
        print("=" * 80)

        sections = detector.detect(column.blocks)

        for section in sections:

            print(f"\n## [{section.name.upper()}]")

            for block in section.blocks:
                print(block.text)


if __name__ == "__main__":
    main()