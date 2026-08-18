from fastapi.testclient import TestClient

from app.api.dependencies import get_job_provider
from app.main import app
from app.models.job import JobOffer
from app.providers.base import JobProvider


client = TestClient(app)


class FakeJobProvider(JobProvider):

    def search_jobs(
        self,
        keywords: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[JobOffer]:

        return [
            JobOffer(
                id="123ABC",
                title="Machine Learning Engineer",
                company="ACME",
                location="75 - Paris",
                contract_type="CDI",
                description="Python SQL MLflow",
                source="france_travail",
                source_url="https://example.com/jobs/123ABC",
            )
        ]


def test_search_jobs_endpoint():

    app.dependency_overrides[get_job_provider] = (
        lambda: FakeJobProvider()
    )

    try:
        response = client.get(
            "/api/jobs/search",
            params={
                "keywords": "machine learning engineer",
                "location": "75101",
                "limit": 10,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1

        assert data[0]["id"] == "123ABC"
        assert (
            data[0]["title"]
            == "Machine Learning Engineer"
        )
        assert data[0]["company"] == "ACME"
        assert data[0]["source"] == "france_travail"

    finally:
        app.dependency_overrides.clear()