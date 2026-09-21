"""Tests for clients/past_weather_comparison.py."""

import httpx
import pytest
import respx

from clients.past_weather_comparison import BASE_URL, fetch_weather_comparison


@pytest.fixture
def mock_actuals_payload():
    """Sample valid response for Best-Match actuals."""
    return {
        "latitude": 34.0901,
        "longitude": -118.4065,
        "hourly_units": {
            "time": "iso8601",
            "temperature_2m": "°F",
            "precipitation": "inch",
        },
        "hourly": {
            "time": ["2026-09-14T00:00", "2026-09-14T01:00"],
            "temperature_2m": [70.0, 68.5],
            "precipitation": [0.0, 0.0],
        },
    }


@pytest.fixture
def mock_forecast_payload():
    """Sample valid response for GEM model forecast."""
    return {
        "latitude": 34.0901,
        "longitude": -118.4065,
        "hourly_units": {
            "time": "iso8601",
            "temperature_2m": "°F",
            "precipitation": "inch",
        },
        "hourly": {
            "time": ["2026-09-14T00:00", "2026-09-14T01:00"],
            "temperature_2m": [72.1, 69.8],
            "precipitation": [0.0, 0.01],
        },
    }


@pytest.mark.asyncio
@respx.mock
async def test_fetch_weather_comparison_success(
    mock_actuals_payload, mock_forecast_payload
):
    """Verify both actuals and forecast payloads are retrieved and returned as a tuple."""
    lat, lon = 34.0901, -118.4065

    # 1. Specific route for Forecast (must contain models=gem_seamless)
    respx.get(BASE_URL, params={"models": "gem_seamless"}).respond(
        status_code=200, json=mock_forecast_payload
    )

    # 2. General route for Actuals (matches requests to BASE_URL without models=gem_seamless)
    respx.get(BASE_URL).respond(
        status_code=200, json=mock_actuals_payload
    )

    async with httpx.AsyncClient() as client:
        actuals, forecast = await fetch_weather_comparison(
            client=client, latitude=lat, longitude=lon
        )

    # Verify actuals response parsing
    assert actuals["hourly"]["temperature_2m"] == [70.0, 68.5]

    # Verify forecast response parsing
    assert forecast["hourly"]["temperature_2m"] == [72.1, 69.8]


@pytest.mark.asyncio
@respx.mock
async def test_fetch_weather_comparison_http_error():
    """Verify HTTPStatusError is raised if one of the API requests fails."""
    respx.get(BASE_URL).respond(
        status_code=500,
        text="Internal Server Error",
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.HTTPStatusError):
            await fetch_weather_comparison(
                client=client, latitude=34.0901, longitude=-118.4065
            )
