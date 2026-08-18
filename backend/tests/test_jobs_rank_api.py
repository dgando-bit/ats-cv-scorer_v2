from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import get_job_provider
from app.main import app
from app.models.job import JobOffer
from app.providers.base import JobProvider


client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CV_PATH = (
    PROJECT_ROOT
    / "data"
    / "samples"
    / "cv_test.pdf"
)


class FakeJobProvider(JobProvider):

    def search_jobs(
        self,
        keywords: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[JobOffer]:

        return [
            JobOffer(
                id="LOW",
                title="Java Developer",
                description="Java Spring Maven",
                source="test",
            ),
            JobOffer(
                id="HIGH",
                title="Machine Learning Engineer",
                description=(
                    "Python SQL Machine Learning "
                    "Docker MLflow"
                ),
                source="test",
            ),
        ]

    def get_job(
        self,
        job_id: str,
    ) -> JobOffer:
        raise NotImplementedError


def test_rank_jobs_endpoint():

    app.dependency_overrides[get_job_provider] = (
        lambda: FakeJobProvider()
    )

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
                    "location": "75101",
                    "limit": "10",
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert data["candidate_name"] == "Destin GANDO"
        assert len(data["jobs"]) == 2

        assert (
            data["jobs"][0]["match"]["score"]
            >= data["jobs"][1]["match"]["score"]
        )

        assert (
            data["jobs"][0]["job"]["id"]
            == "HIGH"
        )

    finally:
        app.dependency_overrides.clear()

def test_rank_jobs_accepts_pdf_with_generic_content_type():

    app.dependency_overrides[get_job_provider] = (
        lambda: FakeJobProvider()
    )

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
                    "location": "75101",
                    "limit": "5",
                },
            )

        assert response.status_code == 200

    finally:
        app.dependency_overrides.clear()

def test_rank_jobs_rejects_fake_pdf():

    app.dependency_overrides[get_job_provider] = (
        lambda: FakeJobProvider()
    )

    try:
        response = client.post(
            "/api/jobs/rank",
            files={
                "file": (
                    "fake.pdf",
                    b"this is not a pdf",
                    "application/pdf",
                )
            },
            data={
                "keywords": "machine learning engineer",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Only valid PDF files are supported."
        )

    finally:
        app.dependency_overrides.clear()