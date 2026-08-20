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
        == 70.0
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

def test_matching_engine_uses_candidate_knowledge_from_experience():

    cv = CV(
        candidate_name="John Doe",
        title="Machine Learning Engineer",
        contact=Contact(),
        profile="",
        experiences=[
            Experience(
                company="ACME",
                role="ML Engineer",
                start_date="2022",
                end_date="2025",
                description=[
                    "Data Engineering avec Python.",
                    "Computer Vision et Data Science.",
                ],
            ),
        ],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    job = JobOffer(
        title="AI Engineer",
        description="",
        skills=[
            "Data Engineering",
            "Computer Vision",
            "Data Science",
        ],
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert result.details.skills == 100.0

    assert "data engineering" in result.matched_skills
    assert "computer vision" in result.matched_skills
    assert "data science" in result.matched_skills

def test_matching_engine_uses_relevant_experience():

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
                    "Machine Learning and MLOps."
                ],
            ),
            Experience(
                company="Web Corp",
                role="Backend Developer",
                start_date="2018",
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

    job = JobOffer(
        title="AI Engineer",
        description="",
        skills=[
            "Machine Learning",
            "MLOps",
        ],
        experience_required="5 ans",
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert result.details.experience == 40.0

def test_matching_engine_uses_total_experience_when_no_domain_is_specified():

    cv = CV(
        candidate_name="John Doe",
        title="Developer",
        contact=Contact(),
        profile="",
        experiences=[
            Experience(
                company="ACME",
                role="Backend Developer",
                start_date="2020",
                end_date="2024",
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
        title="Developer",
        description="",
        experience_required="4 ans",
        skills=[],
        tools=[],
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert result.details.experience == 100.0

def test_matching_engine_education_with_explicit_cv_level():

    cv = CV(
        candidate_name="John Doe",
        title="AI Engineer",
        contact=Contact(),
        profile="",
        experiences=[],
        education=[
            Education(
                institution="Mines Paris",
                degree="Expert en Ingénierie de l’IA",
                year="2025-2026",
                level="Niveau 7 (BAC+5)",
            )
        ],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[],
    )

    job = JobOffer(
        title="AI Engineer",
        description="",
        education_required="Master",
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert result.details.education == 100.0

def test_dynamic_score_ignores_unused_categories():

    scores = {
        "skills": 100.0,
        "tools": 60.0,
        "experience": 20.0,
        "education": 0.0,
        "languages": 0.0,
    }

    active = {
        "skills": True,
        "tools": True,
        "experience": True,
        "education": False,
        "languages": False,
    }

    score = MatchingEngine._calculate_weighted_score(
        scores=scores,
        active=active,
    )

    assert score == 70.0

def test_dynamic_score_redistributes_weights():

    scores = {
        "skills": 100.0,
        "tools": 50.0,
        "experience": 0.0,
        "education": 0.0,
        "languages": 0.0,
    }

    active = {
        "skills": True,
        "tools": True,
        "experience": False,
        "education": False,
        "languages": False,
    }

    score = MatchingEngine._calculate_weighted_score(
        scores=scores,
        active=active,
    )

    # (100 * 0.40 + 50 * 0.20) / 0.60
    assert score == 83.33

def test_dynamic_score_returns_zero_when_no_category_is_active():

    scores = {
        "skills": 0.0,
        "tools": 0.0,
        "experience": 0.0,
        "education": 0.0,
        "languages": 0.0,
    }

    active = {
        "skills": False,
        "tools": False,
        "experience": False,
        "education": False,
        "languages": False,
    }

    score = MatchingEngine._calculate_weighted_score(
        scores=scores,
        active=active,
    )

    assert score == 0.0

def test_matching_engine_language_aliases():
    cv = CV(
        candidate_name="John Doe",
        title="Developer",
        experiences=[],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[
            "English (C1)",
        ],
    )

    job = JobOffer(
        title="Developer",
        description="",
        languages=[
            "Anglais (B2)",
        ],
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert (
        result.details.languages
        == 100.0
    )


def test_matching_engine_partial_language_level():
    cv = CV(
        candidate_name="John Doe",
        title="Developer",
        experiences=[],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[
            "Anglais (B1)",
        ],
    )

    job = JobOffer(
        title="Developer",
        description="",
        languages=[
            "English (B2)",
        ],
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert (
        result.details.languages
        == 75.0
    )


def test_matching_engine_language_without_candidate_level():
    cv = CV(
        candidate_name="John Doe",
        title="Developer",
        experiences=[],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[
            "English",
        ],
    )

    job = JobOffer(
        title="Developer",
        description="",
        languages=[
            "Anglais (B2)",
        ],
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert (
        result.details.languages
        == 70.0
    )


def test_matching_engine_missing_language():
    cv = CV(
        candidate_name="John Doe",
        title="Developer",
        experiences=[],
        education=[],
        skills=[],
        soft_skills=[],
        tools=[],
        languages=[
            "Français (C2)",
        ],
    )

    job = JobOffer(
        title="Developer",
        description="",
        languages=[
            "English (B2)",
        ],
    )

    result = MatchingEngine().match(
        cv,
        job,
    )

    assert (
        result.details.languages
        == 0.0
    )

    assert (
        result.missing_languages
        == ["anglais"]
    )