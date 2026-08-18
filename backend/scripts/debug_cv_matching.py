from pathlib import Path

from app.services.cv.cv_extractor import CVExtractor


CV_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "samples"
    / "cv_test.pdf"
)


cv = CVExtractor().extract(CV_PATH)


print("\n=== TITLE ===")
print(cv.title)

print("\n=== SKILLS ===")
for skill in cv.skills:
    print(f"- {skill}")

print("\n=== TOOLS ===")
for tool in cv.tools:
    print(f"- {tool}")

print("\n=== EXPERIENCES ===")
for experience in cv.experiences:
    print()
    print("ROLE:", experience.role)
    print("COMPANY:", experience.company)

    for line in experience.description:
        print(f"  - {line}")