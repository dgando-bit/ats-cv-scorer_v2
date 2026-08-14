import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_match_endpoint():

    payload = {
        "cv": {
            "candidate_name": "John Doe",
            "title": "Machine Learning Engineer",
            "contact": {},
            "profile": "",
            "experiences": [],
            "education": [],
            "skills": [
                "Python",
                "Machine Learning",
            ],
            "soft_skills": [],
            "tools": [
                "Docker",
                "MLflow",
            ],
            "languages": [
                "English",
            ],
        },
        "job": {
            "title": "Machine Learning Engineer",
            "company": "ACME",
            "location": "Paris",
            "contract_type": "CDI",
            "description": (
                "Nous recherchons un Machine Learning Engineer."
            ),
            "skills": [
                "Python",
                "Machine Learning",
                "SQL",
            ],
            "tools": [
                "Docker",
                "Kubernetes",
            ],
            "soft_skills": [],
            "languages": [
                "English",
            ],
            "experience_required": None,
            "education_required": None,
            "source": "test",
            "source_url": None,
        },
    }

    response = client.post(
        "/api/match",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "score" in data
    assert "details" in data

    assert data["details"]["skills"] == pytest.approx(
        66.67,
        abs=0.01,
    )

    assert data["details"]["tools"] == 50.0
    assert data["details"]["languages"] == 100.0

    assert "sql" in data["missing_skills"]
    assert "kubernetes" in data["missing_tools"]

    assert "python" in data["matched_skills"]
    assert "docker" in data["matched_tools"]