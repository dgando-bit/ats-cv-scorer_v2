from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CV_PATH = (
    PROJECT_ROOT
    / "data"
    / "samples"
    / "cv_test.pdf"
)


def test_analyze_endpoint():

    job_text = """
    Nous recherchons un Machine Learning Engineer.

    Compétences requises :
    Python, SQL, Machine Learning.

    Docker, MLflow et Kubernetes sont utilisés.

    Formation Bac+5.

    Anglais professionnel.
    """

    with CV_PATH.open("rb") as file:

        response = client.post(
            "/api/analyze",
            files={
                "file": (
                    "cv_test.pdf",
                    file,
                    "application/pdf",
                )
            },
            data={
                "job_text": job_text,
                "job_title": "Machine Learning Engineer",
                "company": "ACME",
                "location": "Paris",
                "contract_type": "CDI",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert "score" in data
    assert "details" in data

    assert data["score"] > 0

    assert "python" in data["matched_skills"]

    assert "docker" in data["matched_tools"]

    assert "kubernetes" in data["missing_tools"]

def test_analyze_endpoint_rejects_non_pdf():

    response = client.post(
        "/api/analyze",
        files={
            "file": (
                "cv.txt",
                b"fake cv",
                "text/plain",
            )
        },
        data={
            "job_text": "Python developer",
        },
    )

    assert response.status_code == 400