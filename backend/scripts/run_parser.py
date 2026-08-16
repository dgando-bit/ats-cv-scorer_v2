import sys

from app.services.document_parser import DocumentParser


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/test_parser.py <file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        text = DocumentParser.parse(file_path)

        print("=" * 80)
        print("EXTRACTED TEXT")
        print("=" * 80)
        print(text)

        print("\n" + "=" * 80)
        print(f"Characters: {len(text)}")
        print(f"Lines: {len(text.splitlines())}")
        print("=" * 80)

    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()