from app.models.cv import CV, Contact, Experience
from app.services.matching.relevant_experience_calculator import (
    RelevantExperienceCalculator,
)


def test_calculate_relevant_experience_years():

    cv = CV(
        candidate_name="John Doe",
        title="Machine Learning Engineer",
        contact=Contact(),
        profile="",
        experiences=[
            Experience(
                company="AI Corp",
                role="Machine Learning Engineer",
                start_date="2023",
                end_date="2025",
                description=[
                    "Machine Learning, MLOps and Python."
                ],
            ),
            Experience(
                company="Web Corp",
                role="Backend Developer",
                start_date="2020",
                end_date="2023",
                description=[
                    "REST APIs and PostgreSQL."
                ],
            ),
        ],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    calculator = RelevantExperienceCalculator()

    years = calculator.calculate(
        cv=cv,
        required_terms=[
            "machine learning",
            "mlops",
        ],
    )

    assert years == 2.0

def test_calculate_relevant_experience_across_multiple_jobs():

    cv = CV(
        candidate_name="John Doe",
        title="AI Engineer",
        contact=Contact(),
        profile="",
        experiences=[
            Experience(
                company="AI Corp",
                role="ML Engineer",
                start_date="2022",
                end_date="2024",
                description=[
                    "Machine Learning and MLOps."
                ],
            ),
            Experience(
                company="Data Corp",
                role="Data Scientist",
                start_date="2020",
                end_date="2022",
                description=[
                    "Machine Learning and NLP."
                ],
            ),
        ],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    calculator = RelevantExperienceCalculator()

    years = calculator.calculate(
        cv=cv,
        required_terms=[
            "machine learning",
        ],
    )

    assert years == 4.0

def test_calculate_relevant_experience_returns_zero():

    cv = CV(
        candidate_name="John Doe",
        title="Developer",
        contact=Contact(),
        profile="",
        experiences=[
            Experience(
                company="Web Corp",
                role="Backend Developer",
                start_date="2020",
                end_date="2024",
                description=[
                    "REST APIs and PostgreSQL."
                ],
            ),
        ],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    calculator = RelevantExperienceCalculator()

    years = calculator.calculate(
        cv=cv,
        required_terms=[
            "machine learning",
        ],
    )

    assert years == 0.0