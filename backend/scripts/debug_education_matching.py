from pathlib import Path

from app.services.cv.cv_extractor import CVExtractor


CV_PATH = Path(
    "data/samples/cv_test.pdf"
)


def main():

    extractor = CVExtractor()

    cv = extractor.extract(
        str(CV_PATH)
    )

    print("\n=== EDUCATION ===")

    for education in cv.education:

        print()
        print("INSTITUTION:", education.institution)
        print("DEGREE:", education.degree)
        print("YEAR:", education.year)
        print("LEVEL:", education.level)

if __name__ == "__main__":
    main()