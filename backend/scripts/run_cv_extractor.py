import json
import sys

from app.services.cv_extractor import CVExtractor


def main():

    if len(sys.argv) != 2:
        print(
            "Usage: uv run python "
            "scripts/run_cv_extractor.py <cv.pdf>"
        )
        sys.exit(1)

    file_path = sys.argv[1]

    extractor = CVExtractor()

    cv = extractor.extract(file_path)

    print("=" * 80)
    print("STRUCTURED CV")
    print("=" * 80)

    print(
        json.dumps(
            cv.model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()