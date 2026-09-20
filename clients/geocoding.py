import httpx

from .base import make_request


async def get_coordinates_by_zip_code(client: httpx.AsyncClient, zip_code: str) -> dict:
    """Fetch latitude, longitude, and place details for a given US ZIP code."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": zip_code,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    data = await make_request(client, url, params)

    if not data.get("results"):
        raise ValueError(f"No location found for ZIP code: {zip_code}")

    result = data["results"][0]
    return {
        "name": result.get("name"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
        "admin1": result.get("admin1"),
        "country": result.get("country"),
    }
