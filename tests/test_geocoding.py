import httpx
import pytest
import respx
from clients.geocoding import get_coordinates_by_zip_code


@respx.mock
async def test_get_coordinates_by_zip_code_success():
    """Verify successful ZIP lookup extracts location parameters correctly."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    mock_payload = {
        "results": [
            {
                "name": "Beverly Hills",
                "latitude": 34.0901,
                "longitude": -118.4065,
                "admin1": "California",
                "country": "United States",
            }
        ]
    }
    respx.get(url).respond(json=mock_payload)

    async with httpx.AsyncClient() as client:
        location = await get_coordinates_by_zip_code(client, "90210")

        assert location["name"] == "Beverly Hills"
        assert location["latitude"] == 34.0901
        assert location["longitude"] == -118.4065
        assert location["admin1"] == "California"


@respx.mock
async def test_get_coordinates_by_zip_code_no_results():
    """Verify ValueError is raised when no results are found for a ZIP code."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    respx.get(url).respond(json={"results": []})

    async with httpx.AsyncClient() as client:
        with pytest.raises(ValueError, match="No location found for ZIP code"):
            await get_coordinates_by_zip_code(client, "00000")
