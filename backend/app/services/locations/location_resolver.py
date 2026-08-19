import re

import httpx


class LocationResolver:

    BASE_URL = (
        "https://geo.api.gouv.fr/communes"
    )

    def resolve(
        self,
        location: str | None,
    ) -> str | None:

        if not location:
            return None

        value = location.strip()

        if not value:
            return None

        params: dict[str, str] = {
            "fields": "nom,code,codesPostaux",
            "format": "json",
        }

        # Code postal français
        if re.fullmatch(r"\d{5}", value):
            params["codePostal"] = value

        # Nom de commune
        else:
            params["nom"] = value
            params["boost"] = "population"

        response = httpx.get(
            self.BASE_URL,
            params=params,
            timeout=10.0,
        )

        response.raise_for_status()

        communes = response.json()

        if not communes:
            return None

        return communes[0].get("code")