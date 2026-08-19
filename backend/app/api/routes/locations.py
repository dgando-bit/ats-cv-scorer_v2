from fastapi import APIRouter, Query

from app.services.locations.location_resolver import (
    LocationResolver,
    LocationSuggestion,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)

resolver = LocationResolver()


@router.get(
    "/search",
    response_model=list[LocationSuggestion],
)
def search_locations(
    q: str = Query(
        ...,
        min_length=2,
        description="Nom de ville ou code postal",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=20,
    ),
) -> list[LocationSuggestion]:

    return resolver.search(
        query=q,
        limit=limit,
    )