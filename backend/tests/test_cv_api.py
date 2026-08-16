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


def test_extract_cv_endpoint():

    with CV_PATH.open("rb") as file:

        response = client.post(
            "/api/cv/extract",
            files={
                "file": (
                    "cv_test.pdf",
                    file,
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_name"] == "Destin GANDO"
    assert data["title"] == "MACHINE LEARNING ENGINEER"

    assert data["contact"]["email"] == (
        "d.gbakary@outlook.com"
    )

    assert len(data["experiences"]) == 4
    assert len(data["education"]) == 4

    assert "Python" in data["tools"]

def test_extract_cv_rejects_non_pdf():

    response = client.post(
        "/api/cv/extract",
        files={
            "file": (
                "cv.txt",
                b"fake cv",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only PDF files are supported."
    )