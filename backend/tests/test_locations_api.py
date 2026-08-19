from fastapi.testclient import TestClient

from app.api.routes import locations
from app.main import app
from app.services.locations.location_resolver import (
    LocationSuggestion,
)


client = TestClient(app)


def test_search_locations_api(
    monkeypatch,
):
    def fake_search(
        query: str,
        limit: int = 10,
    ):
        return [
            LocationSuggestion(
                label=(
                    "Paris 1er Arrondissement "
                    "(75001)"
                ),
                city="Paris 1er Arrondissement",
                postal_code="75001",
                insee_code="75101",
            )
        ]

    monkeypatch.setattr(
        locations.resolver,
        "search",
        fake_search,
    )

    response = client.get(
        "/api/locations/search",
        params={
            "q": "Paris",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["postal_code"] == "75001"
    assert data[0]["insee_code"] == "75101"