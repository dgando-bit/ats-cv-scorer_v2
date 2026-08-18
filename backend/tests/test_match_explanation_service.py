from app.models.job import JobOffer
from app.models.match import MatchDetails, MatchResult
from app.services.matching.match_explanation_service import (
    MatchExplanationService,
)


def test_explain_good_match_with_missing_tools():

    job = JobOffer(
        title="AI Engineer",
        description="",
        skills=[
            "machine learning",
            "llm",
            "rag",
        ],
        tools=[
            "pytorch",
            "azure",
            "spark",
        ],
        experience_required="5 ans",
    )

    match = MatchResult(
        score=70.0,
        details=MatchDetails(
            skills=100.0,
            tools=60.0,
            experience=20.0,
            education=0.0,
            languages=0.0,
        ),
        matched_skills=[
            "machine learning",
            "llm",
            "rag",
        ],
        missing_skills=[],
        matched_tools=[
            "pytorch",
        ],
        missing_tools=[
            "azure",
            "spark",
        ],
    )

    explanation = MatchExplanationService().explain(
        job=job,
        match=match,
    )

    assert explanation.summary

    assert any(
        "compétences" in value.lower()
        for value in explanation.strengths
    )

    assert any(
        "expérience" in value.lower()
        for value in explanation.weaknesses
    )

    assert any(
        "azure" in value.lower()
        for value in explanation.recommendations
    )


def test_explain_high_match():

    job = JobOffer(
        title="Data Engineer",
        description="",
        skills=[
            "python",
            "sql",
        ],
        tools=[
            "docker",
            "postgresql",
        ],
        education_required="Master",
    )

    match = MatchResult(
        score=100.0,
        details=MatchDetails(
            skills=100.0,
            tools=100.0,
            experience=0.0,
            education=100.0,
            languages=0.0,
        ),
        matched_skills=[
            "python",
            "sql",
        ],
        matched_tools=[
            "docker",
            "postgresql",
        ],
    )

    explanation = MatchExplanationService().explain(
        job=job,
        match=match,
    )

    assert explanation.summary
    assert len(explanation.strengths) >= 2
    assert explanation.weaknesses == []