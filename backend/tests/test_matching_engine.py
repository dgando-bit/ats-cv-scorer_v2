import pytest
from app.models.cv import (
    CV,
    Contact,
    Experience,
    Education,
)
from app.models.job import JobOffer
from app.services.matching.matching_engine import MatchingEngine
from app.models.match import MatchDetails, MatchResult

def test_matching_engine_basic_score():

    cv = CV(
        candidate_name="John Doe",
        title="Machine Learning Engineer",
        contact=Contact(),
        profile="",
        experiences=[],
        education=[],
        skills=[
            "Python",
            "Machine Learning",
            "SQL",
        ],
        soft_skills=[],
        tools=[
            "Docker",
            "MLflow",
            "PostgreSQL",
        ],
        languages=[
            "English",
        ],
    )

    job = JobOffer(
        title="Machine Learning Engineer",
        description="ML Engineer position",
        skills=[
            "Python",
            "Machine Learning",
            "SQL",
            "Spark",
        ],
        tools=[
            "Docker",
            "MLflow",
            "Kubernetes",
        ],
        languages=[
            "English",
        ],
    )

    engine = MatchingEngine()

    result = engine.match(
        cv,
        job,
    )

    assert result.details.skills == 75.0

    assert result.details.tools == pytest.approx(
        66.67,
        abs=0.01,
    )

    assert result.details.languages == 100.0

    assert "spark" in result.missing_skills

    assert "kubernetes" in result.missing_tools

def test_matching_engine_uses_skill_aliases():

    cv = CV(
        candidate_name="John Doe",
        title="Data Scientist",
        contact=Contact(),
        profile="",
        experiences=[],
        education=[],
        skills=[
            "ML",
        ],
        soft_skills=[],
        tools=[
            "sklearn",
            "Postgres",
        ],
        languages=[],
    )

    job = JobOffer(
        title="Data Scientist",
        description="",
        skills=[
            "Machine Learning",
        ],
        tools=[
            "Scikit-Learn",
            "PostgreSQL",
        ],
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert result.details.skills == 100.0
    assert result.details.tools == 100.0

def test_matching_engine_experience_score():

    cv = CV(
        candidate_name="John Doe",
        title="Data Engineer",
        contact=Contact(),
        profile="",
        experiences=[
            Experience(
                company="ACME",
                role="Data Engineer",
                start_date="2021",
                end_date="2025",
                description=[],
            ),
        ],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    job = JobOffer(
        title="Data Engineer",
        description="",
        experience_required="3 ans",
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert (
        result.details.experience
        == 100.0
    )

def test_matching_engine_partial_experience_score():

    cv = CV(
        candidate_name="John Doe",
        title="Data Engineer",
        contact=Contact(),
        profile="",
        experiences=[
            Experience(
                company="ACME",
                role="Data Engineer",
                start_date="2023",
                end_date="2025",
                description=[],
            ),
        ],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    job = JobOffer(
        title="Senior Data Engineer",
        description="",
        experience_required="4 ans",
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert (
        result.details.experience
        == 50.0
    )

def test_matching_engine_education_score():

    cv = CV(
        candidate_name="John Doe",
        title="Data Scientist",
        contact=Contact(),
        profile="",
        experiences=[],
        education=[
            Education(
                institution="Université",
                degree="Master Data Science",
                year="2024",
            ),
        ],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    job = JobOffer(
        title="Data Scientist",
        description="",
        education_required="Bac+5",
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert (
        result.details.education
        == 100.0
    )

def test_matching_engine_partial_education_score():

    cv = CV(
        candidate_name="John Doe",
        title="Data Analyst",
        contact=Contact(),
        profile="",
        experiences=[],
        education=[
            Education(
                institution="Université",
                degree="Bachelor Data",
                year="2022",
            ),
        ],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    job = JobOffer(
        title="Data Scientist",
        description="",
        education_required="Bac+5",
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert (
        result.details.education
        == 60.0
    )

def test_match_result_model():
    result = MatchResult(
        score=82.5,
        details=MatchDetails(
            skills=80,
            tools=75,
            languages=100,
            experience=90,
            education=100,
        ),
        matched_skills=["python"],
        missing_skills=["spark"],
    )

    assert result.score == 82.5
    assert result.details.skills == 80
    assert result.missing_skills == ["spark"]

def test_matching_skills_can_be_found_in_cv_tools():

    cv = CV(
        candidate_name="John Doe",
        title="Machine Learning Engineer",
        contact=Contact(),
        profile="",
        experiences=[],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[
            "Python",
            "SQL",
        ],
        languages=[],
    )

    job = JobOffer(
        title="Machine Learning Engineer",
        description="",
        skills=[
            "Python",
            "SQL",
        ],
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert result.details.skills == 100.0
    assert "python" in result.matched_skills
    assert "sql" in result.matched_skills

def test_empty_job_categories_do_not_inflate_score():

    cv = CV(
        candidate_name="John Doe",
        title="Developer",
        skills=[],
        tools=[],
        languages=[],
        experiences=[],
        education=[],
    )

    job = JobOffer(
        title="Product Builder",
        description="Stage Product Builder",
        skills=[],
        tools=[],
        languages=["anglais", "français"],
        experience_required=None,
        education_required="Bac+5",
    )

    result = MatchingEngine().match(cv, job)

    assert result.details.skills == 0
    assert result.details.tools == 0
    assert result.details.languages == 0
    assert result.details.experience == 0
    assert result.details.education == 0

    assert result.score == 0

    assert result.matched_skills == []
    assert result.missing_skills == []

    assert result.matched_tools == []
    assert result.missing_tools == []

    assert set(result.missing_languages) == {
        "anglais",
        "français",
    }