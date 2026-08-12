import sys

from app.services.document_parser import DocumentParser
from app.services.resume_ner import ResumeNER


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/run_ner.py <cv_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    print("Loading document...")

    text = DocumentParser.parse(file_path)

    print(f"Extracted {len(text)} characters.")

    print("\nLoading NER model...")

    ner = ResumeNER()

    print("Running NER...\n")

    entities = ner.extract(text)

    print("=" * 80)
    print("EXTRACTED ENTITIES")
    print("=" * 80)

    for entity in entities:
        print(
            f"{entity['label']:15} "
            f"{entity['score']:.3f}  "
            f"{entity['text']}"
        )

    print("=" * 80)
    print(f"Total entities: {len(entities)}")


if __name__ == "__main__":
    main()