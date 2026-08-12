from app.models.cv import (
    CVProfile,
    ExperienceItem,
    LanguageItem,
)


def test_cv_profile_creation():

    cv = CVProfile(
        profile="Machine Learning Engineer",
        experiences=[
            ExperienceItem(
                company="Airweb - Paragon ID",
                role="Développeur Back-end",
                start_date="2021",
                end_date="2025",
                description=[
                    "Conception d'APIs REST",
                    "Data Engineering",
                ],
            )
        ],
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        languages=[
            LanguageItem(
                language="Anglais",
                level="B2",
            )
        ],
    )

    assert cv.profile == "Machine Learning Engineer"

    assert len(cv.experiences) == 1
    assert cv.experiences[0].company == "Airweb - Paragon ID"

    assert "Python" in cv.skills

    assert cv.languages[0].language == "Anglais"
    assert cv.languages[0].level == "B2"