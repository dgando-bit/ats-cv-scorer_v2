from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_job_search_pipeline,
)
from app.main import app
from app.models.match import (
    MatchDetails,
    MatchExplanation,
    MatchResult,
)
from app.models.ranking import (
    JobRankingResult,
    RankedJob,
)
from app.models.job import JobOffer


client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CV_PATH = (
    PROJECT_ROOT
    / "data"
    / "samples"
    / "cv_test.pdf"
)


class FakeJobSearchPipeline:
    def search_and_rank(
        self,
        cv,
        keywords,
        location=None,
        insee_code=None,
        provider_limit=50,
        retrieval_top_k=20,
        final_limit=10,
    ) -> JobRankingResult:
        job = JobOffer(
            id="test-job-1",
            title="Machine Learning Engineer",
            company="ACME",
            location="75 - Paris",
            contract_type="CDI",
            description=(
                "Développement et déploiement "
                "de modèles de machine learning."
            ),
            skills=[
                "machine learning",
                "python",
            ],
            tools=[
                "scikit-learn",
            ],
            languages=[],
            experience_required="2 ans",
            education_required="BAC+5",
            source="france_travail",
            source_url=(
                "https://example.com/jobs/"
                "test-job-1"
            ),
        )

        match = MatchResult(
            score=90.0,
            details=MatchDetails(
                skills=100.0,
                tools=100.0,
                languages=0.0,
                experience=50.0,
                education=100.0,
            ),
            matched_skills=[
                "machine learning",
                "python",
            ],
            missing_skills=[],
            matched_tools=[
                "scikit-learn",
            ],
            missing_tools=[],
            matched_languages=[],
            missing_languages=[],
        )

        explanation = MatchExplanation(
            summary=(
                "Très bonne compatibilité "
                "avec l'offre."
            ),
            strengths=[
                (
                    "Très bonne couverture "
                    "des compétences demandées."
                ),
            ],
            weaknesses=[],
            recommendations=[],
        )

        ranked_job = RankedJob(
            job=job,
            match=match,
            semantic_score=0.82,
            relevance_score=0.95,
            explanation=explanation,
        )

        return JobRankingResult(
            candidate_name=cv.candidate_name,
            jobs=[
                ranked_job,
            ],
        )


def override_pipeline():
    return FakeJobSearchPipeline()


def test_rank_jobs_endpoint():
    app.dependency_overrides[
        get_job_search_pipeline
    ] = override_pipeline

    try:
        with CV_PATH.open("rb") as file:
            response = client.post(
                "/api/jobs/rank",
                files={
                    "file": (
                        "cv_test.pdf",
                        file,
                        "application/pdf",
                    )
                },
                data={
                    "keywords": (
                        "machine learning engineer"
                    ),
                    "location": (
                        "Paris (75002)"
                    ),
                    "insee_code": "75056",
                    "limit": "10",
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert data["candidate_name"]

        assert len(
            data["jobs"]
        ) == 1

        ranked_job = data["jobs"][0]

        assert (
            ranked_job["job"]["id"]
            == "test-job-1"
        )

        assert (
            ranked_job["job"]["title"]
            == "Machine Learning Engineer"
        )

        assert (
            ranked_job["match"]["score"]
            == 90.0
        )

        assert (
            ranked_job["semantic_score"]
            == 0.82
        )

        assert (
            ranked_job["relevance_score"]
            == 0.95
        )

        assert (
            ranked_job[
                "explanation"
            ]["summary"]
            == (
                "Très bonne compatibilité "
                "avec l'offre."
            )
        )

    finally:
        app.dependency_overrides.clear()


def test_rank_jobs_accepts_pdf_with_generic_content_type():
    app.dependency_overrides[
        get_job_search_pipeline
    ] = override_pipeline

    try:
        with CV_PATH.open("rb") as file:
            response = client.post(
                "/api/jobs/rank",
                files={
                    "file": (
                        "cv_test.pdf",
                        file,
                        "application/octet-stream",
                    )
                },
                data={
                    "keywords": (
                        "machine learning engineer"
                    ),
                    "location": (
                        "Paris (75002)"
                    ),
                    "insee_code": "75056",
                    "limit": "5",
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert data["candidate_name"]

        assert len(
            data["jobs"]
        ) == 1

    finally:
        app.dependency_overrides.clear()


def test_rank_jobs_rejects_invalid_file():
    app.dependency_overrides[
        get_job_search_pipeline
    ] = override_pipeline

    try:
        response = client.post(
            "/api/jobs/rank",
            files={
                "file": (
                    "not-a-pdf.txt",
                    b"this is not a pdf",
                    "text/plain",
                )
            },
            data={
                "keywords": (
                    "machine learning engineer"
                ),
                "limit": "5",
            },
        )

        assert response.status_code in {
            400,
            415,
            422,
        }

    finally:
        app.dependency_overrides.clear()