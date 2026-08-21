import os
import time
from abc import ABC

import httpx

from app.models.job import JobOffer
from app.providers.base import JobProvider
from app.services.locations.location_resolver import (
    LocationResolver,
)


class FranceTravailProvider(
    JobProvider,
    ABC,
):

    TOKEN_URL = (
        "https://entreprise.francetravail.fr/"
        "connexion/oauth2/access_token"
    )

    SEARCH_URL = (
        "https://api.francetravail.io/"
        "partenaire/offresdemploi/v2/offres/search"
    )

    DETAIL_URL = (
        "https://api.francetravail.io/"
        "partenaire/offresdemploi/v2/offres"
    )

    DEFAULT_SCOPE = (
        "api_offresdemploiv2 o2dsoffre"
    )

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        scope: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:

        self.location_resolver = (
            LocationResolver()
        )

        self.client_id = (
            client_id
            or os.getenv(
                "FRANCE_TRAVAIL_CLIENT_ID"
            )
        )

        self.client_secret = (
            client_secret
            or os.getenv(
                "FRANCE_TRAVAIL_CLIENT_SECRET"
            )
        )

        self.scope = (
            scope
            or os.getenv(
                "FRANCE_TRAVAIL_SCOPE",
                self.DEFAULT_SCOPE,
            )
        )

        if not self.client_id:
            raise ValueError(
                "FRANCE_TRAVAIL_CLIENT_ID "
                "is missing."
            )

        if not self.client_secret:
            raise ValueError(
                "FRANCE_TRAVAIL_CLIENT_SECRET "
                "is missing."
            )

        self.client = (
            client
            or httpx.Client(
                timeout=20.0
            )
        )

        self._access_token: str | None = None

        self._token_expires_at = 0.0

    # =============================================================
    # Authentication
    # =============================================================

    def _get_access_token(
        self,
    ) -> str:

        # ---------------------------------------------------------
        # Réutiliser le token tant qu'il est valide.
        # ---------------------------------------------------------

        if (
            self._access_token
            and time.time()
            < self._token_expires_at
        ):
            return self._access_token

        response = self.client.post(
            self.TOKEN_URL,
            params={
                "realm": "/partenaire",
            },
            data={
                "grant_type": (
                    "client_credentials"
                ),
                "client_id": (
                    self.client_id
                ),
                "client_secret": (
                    self.client_secret
                ),
                "scope": (
                    self.scope
                ),
            },
            headers={
                "Content-Type": (
                    "application/"
                    "x-www-form-urlencoded"
                ),
            },
        )

        response.raise_for_status()

        if not response.content:
            raise RuntimeError(
                "France Travail returned "
                "an empty authentication response."
            )

        try:
            data = response.json()

        except ValueError as exc:
            raise RuntimeError(
                "France Travail returned "
                "an invalid authentication response."
            ) from exc

        access_token = data.get(
            "access_token"
        )

        if not access_token:
            raise RuntimeError(
                "France Travail did not "
                "return an access token."
            )

        expires_in = int(
            data.get(
                "expires_in",
                1200,
            )
        )

        self._access_token = (
            access_token
        )

        # ---------------------------------------------------------
        # Petite marge pour éviter d'utiliser
        # un token sur le point d'expirer.
        # ---------------------------------------------------------

        self._token_expires_at = (
            time.time()
            + max(
                expires_in - 60,
                0,
            )
        )

        return access_token

    # =============================================================
    # Search
    # =============================================================

    def search_jobs(
        self,
        keywords: str,
        location: str | None = None,
        insee_code: str | None = None,
        limit: int = 20,
    ) -> list[JobOffer]:

        token = (
            self._get_access_token()
        )

        limit = max(
            1,
            min(
                limit,
                100,
            ),
        )

        params: dict[
            str,
            str,
        ] = {
            "motsCles": keywords,
            "range": (
                f"0-{limit - 1}"
            ),
        }

        # ---------------------------------------------------------
        # Localisation
        # ---------------------------------------------------------

        if insee_code:
            # -----------------------------------------------------
            # Cas idéal :
            # l'utilisateur a sélectionné une suggestion
            # de l'autocomplétion.
            # -----------------------------------------------------

            params["commune"] = (
                insee_code
            )

        elif location:
            # -----------------------------------------------------
            # Saisie libre :
            # on tente de résoudre la ville vers son code INSEE.
            # -----------------------------------------------------

            normalized_location = (
                location.strip()
            )

            if normalized_location:
                commune_code = (
                    self
                    .location_resolver
                    .resolve(
                        normalized_location
                    )
                )

                # -------------------------------------------------
                # IMPORTANT :
                #
                # Une localisation a été demandée mais elle
                # n'existe pas / n'est pas reconnue.
                #
                # On ne doit surtout pas retirer le filtre et
                # rechercher ensuite dans toute la France.
                # -------------------------------------------------

                if not commune_code:
                    print(
                        "[france-travail] "
                        "Unknown location: "
                        f"{normalized_location!r}",
                        flush=True,
                    )

                    return []

                params["commune"] = (
                    commune_code
                )

        # ---------------------------------------------------------
        # Appel France Travail
        # ---------------------------------------------------------

        response = self.client.get(
            self.SEARCH_URL,
            params=params,
            headers={
                "Authorization": (
                    f"Bearer {token}"
                ),
                "Accept": (
                    "application/json"
                ),
            },
        )

        # ---------------------------------------------------------
        # France Travail peut retourner une réponse sans contenu
        # lorsqu'aucune offre n'est trouvée.
        # ---------------------------------------------------------

        if response.status_code == 204:
            return []

        response.raise_for_status()

        # ---------------------------------------------------------
        # Même avec un statut HTTP valide, ne jamais supposer
        # automatiquement que le body contient du JSON.
        # ---------------------------------------------------------

        if not response.content:
            return []

        try:
            payload = (
                response.json()
            )

        except ValueError as exc:
            content_type = (
                response.headers.get(
                    "content-type",
                    "",
                )
            )

            print(
                "[france-travail] "
                "Invalid JSON response. "
                f"status={response.status_code}, "
                f"content_type={content_type!r}",
                flush=True,
            )

            raise RuntimeError(
                "France Travail returned "
                "an invalid search response."
            ) from exc

        # ---------------------------------------------------------
        # Extraction des résultats
        # ---------------------------------------------------------

        if isinstance(
            payload,
            dict,
        ):
            results = payload.get(
                "resultats",
                [],
            )

        elif isinstance(
            payload,
            list,
        ):
            results = payload

        else:
            results = []

        if not isinstance(
            results,
            list,
        ):
            return []

        return [
            self._to_job_offer(
                item
            )
            for item in results
            if isinstance(
                item,
                dict,
            )
        ]

    # =============================================================
    # Job detail
    # =============================================================

    def get_job(
        self,
        job_id: str,
    ) -> JobOffer:

        token = (
            self._get_access_token()
        )

        response = self.client.get(
            f"{self.DETAIL_URL}/{job_id}",
            headers={
                "Authorization": (
                    f"Bearer {token}"
                ),
                "Accept": (
                    "application/json"
                ),
            },
        )

        response.raise_for_status()

        if not response.content:
            raise RuntimeError(
                "France Travail returned "
                "an empty job response."
            )

        try:
            payload = (
                response.json()
            )

        except ValueError as exc:
            raise RuntimeError(
                "France Travail returned "
                "an invalid job response."
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "France Travail returned "
                "an unexpected job response."
            )

        return (
            self._to_job_offer(
                payload
            )
        )

    # =============================================================
    # Mapping France Travail -> JobOffer
    # =============================================================

    @staticmethod
    def _to_job_offer(
        data: dict,
    ) -> JobOffer:

        company_data = (
            data.get(
                "entreprise"
            )
            or {}
        )

        location_data = (
            data.get(
                "lieuTravail"
            )
            or {}
        )

        origin_data = (
            data.get(
                "origineOffre"
            )
            or {}
        )

        return JobOffer(
            id=(
                data.get(
                    "id"
                )
            ),
            title=(
                data.get(
                    "intitule"
                )
                or ""
            ),
            company=(
                company_data.get(
                    "nom"
                )
            ),
            location=(
                location_data.get(
                    "libelle"
                )
            ),
            contract_type=(
                data.get(
                    "typeContratLibelle"
                )
                or data.get(
                    "typeContrat"
                )
            ),
            description=(
                data.get(
                    "description"
                )
                or ""
            ),
            source=(
                "france_travail"
            ),
            source_url=(
                origin_data.get(
                    "urlOrigine"
                )
            ),
        )