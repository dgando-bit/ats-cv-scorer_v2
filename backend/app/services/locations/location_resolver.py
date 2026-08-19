import re

import httpx
from pydantic import BaseModel


class LocationSuggestion(BaseModel):
    label: str
    city: str
    postal_code: str | None = None
    insee_code: str

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

    def search(
            self,
            query: str,
            limit: int = 10,
    ) -> list[LocationSuggestion]:

        value = query.strip()

        if len(value) < 2:
            return []

        params: dict[str, str | int] = {
            "fields": "nom,code,codesPostaux",
            "format": "json",
            "limit": limit,
        }

        if re.fullmatch(r"\d{2,5}", value):
            params["codePostal"] = value
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

        suggestions: list[LocationSuggestion] = []

        for commune in communes:
            city = commune.get("nom")
            insee_code = commune.get("code")

            if not city or not insee_code:
                continue

            postal_codes = (
                    commune.get("codesPostaux") or []
            )

            # Une commune peut avoir plusieurs codes postaux.
            if postal_codes:
                for postal_code in postal_codes:
                    suggestions.append(
                        LocationSuggestion(
                            label=(
                                f"{city} ({postal_code})"
                            ),
                            city=city,
                            postal_code=postal_code,
                            insee_code=insee_code,
                        )
                    )
            else:
                suggestions.append(
                    LocationSuggestion(
                        label=city,
                        city=city,
                        postal_code=None,
                        insee_code=insee_code,
                    )
                )

            if len(suggestions) >= limit:
                break

        return suggestions[:limit]