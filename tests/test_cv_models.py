from app.models.cv import CV, Contact, Experience


def test_cv_model():

    cv = CV(
        candidate_name="Destin GANDO",
        title="MACHINE LEARNING ENGINEER",
        contact=Contact(
            email="d.gbakary@outlook.com",
            phone="+33 6 70 50 41 98",
            location="Thiais, France",
        ),
        profile="Machine Learning Engineer avec une expérience en développement back-end.",
        experiences=[
            Experience(
                company="Liora",
                role="IA & Machine Learning Engineer",
                start_date="2025",
                end_date="2026",
                description=[
                    "Analyse de données",
                    "Computer Vision",
                    "MLOps",
                ],
            )
        ],
        skills=[
            "Python",
            "Pandas",
            "Scikit-learn",
            "FastAPI",
            "Docker",
        ],
        languages=[
            "Anglais (B2)",
            "LSF (C2)",
        ],
    )

    assert cv.candidate_name == "Destin GANDO"
    assert cv.contact.email == "d.gbakary@outlook.com"
    assert len(cv.experiences) == 1
    assert cv.experiences[0].company == "Liora"
    assert "Python" in cv.skills