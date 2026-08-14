from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_extract_job_endpoint():

    payload = {
        "title": "Machine Learning Engineer",
        "company": "ACME",
        "location": "Paris",
        "contract_type": "CDI",
        "text": (
            "Nous recherchons un Machine Learning Engineer "
            "avec 3 ans d'expérience. "
            "Maîtrise de Python, SQL et Scikit-learn requise. "
            "Docker et MLflow sont appréciés. "
            "Formation Bac+5 en informatique. "
            "Anglais professionnel."
        ),
    }

    response = client.post(
        "/api/job/extract",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Machine Learning Engineer"
    assert data["company"] == "ACME"
    assert data["location"] == "Paris"

    assert "python" in data["skills"]
    assert "sql" in data["skills"]

    assert "scikit-learn" in data["tools"]
    assert "docker" in data["tools"]
    assert "mlflow" in data["tools"]

    assert data["experience_required"] == "3 ans"
    assert data["education_required"].lower() == "bac+5"
    assert "Anglais" in data["languages"]