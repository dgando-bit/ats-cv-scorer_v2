import httpx

from app.providers.france_travail import (
    FranceTravailProvider,
)


def test_search_france_travail_jobs():

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:

        if (
            "access_token"
            in request.url.path
        ):
            return httpx.Response(
                200,
                json={
                    "access_token": "fake-token",
                    "expires_in": 1200,
                },
            )

        assert (
            request.headers[
                "Authorization"
            ]
            == "Bearer fake-token"
        )

        return httpx.Response(
            200,
            json={
                "resultats": [
                    {
                        "id": "123ABC",
                        "intitule": (
                            "Data Engineer"
                        ),
                        "description": (
                            "Python SQL Airflow"
                        ),
                        "entreprise": {
                            "nom": "ACME",
                        },
                        "lieuTravail": {
                            "libelle": (
                                "75 - Paris"
                            ),
                        },
                        "typeContrat": "CDI",
                    },
                ],
            },
        )

    transport = httpx.MockTransport(
        handler
    )

    client = httpx.Client(
        transport=transport
    )

    provider = FranceTravailProvider(
        client_id="client-id",
        client_secret="client-secret",
        client=client,
    )

    jobs = provider.search_jobs(
        keywords="data engineer",
        location="75101",
    )

    assert len(jobs) == 1

    job = jobs[0]

    assert job.id == "123ABC"
    assert job.title == "Data Engineer"
    assert job.company == "ACME"
    assert job.location == "75 - Paris"
    assert job.contract_type == "CDI"
    assert job.source == "france_travail"