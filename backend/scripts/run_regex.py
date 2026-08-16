import sys

from app.services.document_parser import DocumentParser
from app.services.regex_extractor import RegexExtractor


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/run_regex.py <cv_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    text = DocumentParser.parse(file_path)

    extractor = RegexExtractor()
    result = extractor.extract(text)

    print("=" * 80)
    print("REGEX EXTRACTION")
    print("=" * 80)

    for key, values in result.items():
        print(f"\n{key.upper()}")

        for value in values:
            print(f"  - {value}")

    print("=" * 80)


if __name__ == "__main__":
    main()