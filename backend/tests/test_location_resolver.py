import httpx

from app.services.locations.location_resolver import (
    LocationResolver,
)


def test_resolve_location_from_postal_code(
    monkeypatch,
):
    resolver = LocationResolver()

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return [
                {
                    "nom": "Paris 1er Arrondissement",
                    "code": "75101",
                    "codesPostaux": ["75001"],
                }
            ]

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "get",
        fake_get,
    )

    result = resolver.resolve("75001")

    assert result == "75101"


def test_resolve_location_from_city_name(
    monkeypatch,
):
    resolver = LocationResolver()

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return [
                {
                    "nom": "Paris",
                    "code": "75056",
                }
            ]

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "get",
        fake_get,
    )

    result = resolver.resolve("Paris")

    assert result == "75056"


def test_resolve_location_returns_none_when_not_found(
    monkeypatch,
):
    resolver = LocationResolver()

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return []

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "get",
        fake_get,
    )

    result = resolver.resolve("Ville inconnue")

    assert result is None

def test_search_locations(
    monkeypatch,
):
    resolver = LocationResolver()

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return [
                {
                    "nom": "Paris 1er Arrondissement",
                    "code": "75101",
                    "codesPostaux": ["75001"],
                },
                {
                    "nom": "Paris 2e Arrondissement",
                    "code": "75102",
                    "codesPostaux": ["75002"],
                },
            ]

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "get",
        fake_get,
    )

    result = resolver.search("Paris")

    assert len(result) == 2

    assert result[0].city == (
        "Paris 1er Arrondissement"
    )

    assert result[0].postal_code == "75001"
    assert result[0].insee_code == "75101"

    assert result[0].label == (
        "Paris 1er Arrondissement (75001)"
    )

def test_search_locations_requires_two_characters():
    resolver = LocationResolver()

    assert resolver.search("P") == []
    assert resolver.search("") == []