"""Tests for clients/current_weather.py."""

import httpx
import pytest
import respx

from clients.base import APIError
from clients.current_weather import OPEN_METEO_FORECAST_URL, get_current_weather


@pytest.fixture
def mock_current_weather_payload():
    """Sample valid response payload matching Open-Meteo current endpoint structure."""
    return {
        "latitude": 34.0901,
        "longitude": -118.4065,
        "generationtime_ms": 0.12,
        "utc_offset_seconds": 0,
        "timezone": "GMT",
        "timezone_abbreviation": "GMT",
        "elevation": 160.0,
        "current_units": {
            "time": "iso8601",
            "interval": "seconds",
            "temperature_2m": "°F",
            "relative_humidity_2m": "%",
            "apparent_temperature": "°F",
            "is_day": "",
            "precipitation": "inch",
            "rain": "inch",
            "showers": "inch",
            "snowfall": "inch",
            "weather_code": "wmo code",
            "cloud_cover": "%",
            "pressure_msl": "hPa",
            "surface_pressure": "hPa",
            "wind_speed_10m": "mph",
            "wind_direction_10m": "°",
            "wind_gusts_10m": "mph",
        },
        "current": {
            "time": "2026-09-20T23:00",
            "interval": 900,
            "temperature_2m": 72.5,
            "relative_humidity_2m": 45,
            "apparent_temperature": 71.8,
            "is_day": 1,
            "precipitation": 0.0,
            "rain": 0.0,
            "showers": 0.0,
            "snowfall": 0.0,
            "weather_code": 0,
            "cloud_cover": 10,
            "pressure_msl": 1013.2,
            "surface_pressure": 995.4,
            "wind_speed_10m": 8.4,
            "wind_direction_10m": 210,
            "wind_gusts_10m": 12.1,
        },
        "daily_units": {
            "time": "iso8601",
            "sunrise": "iso8601",
            "sunset": "iso8601",
            "moonrise": "iso8601",
            "moonset": "iso8601",
            "moon_phase": "fraction",
            "weather_code": "wmo code",
            "temperature_2m_max": "°F",
            "temperature_2m_min": "°F",
            "apparent_temperature_min": "°F",
            "apparent_temperature_max": "°F",
            "uv_index_max": "",
            "uv_index_clear_sky_max": "",
            "daylight_duration": "s",
            "sunshine_duration": "s",
            "rain_sum": "inch",
            "showers_sum": "inch",
            "snowfall_sum": "inch",
            "precipitation_sum": "inch",
            "precipitation_hours": "h",
            "precipitation_probability_max": "%",
            "wind_speed_10m_max": "mph",
            "wind_gusts_10m_max": "mph",
            "wind_direction_10m_dominant": "°",
            "shortwave_radiation_sum": "MJ/m²",
            "et0_fao_evapotranspiration": "inch",
        },
        "daily": {
            "time": ["2026-09-20"],
            "sunrise": ["2026-09-20T04:48"],
            "sunset": ["2026-09-20T17:09"],
            "moonrise": ["2026-09-20T15:01"],
            "moonset": ["2026-09-20T22:05"],
            "moon_phase": [0.3],
            "weather_code": [95],
            "temperature_2m_max": [70.4],
            "temperature_2m_min": [56.0],
            "apparent_temperature_min": [51.2],
            "apparent_temperature_max": [66.4],
            "uv_index_max": [3.55],
            "uv_index_clear_sky_max": [4.15],
            "daylight_duration": [44471.71],
            "sunshine_duration": [4895.09],
            "rain_sum": [0.264],
            "showers_sum": [0.0],
            "snowfall_sum": [0.0],
            "precipitation_sum": [0.268],
            "precipitation_hours": [7],
            "precipitation_probability_max": [45],
            "wind_speed_10m_max": [13.4],
            "wind_gusts_10m_max": [30.2],
            "wind_direction_10m_dominant": [257],
            "shortwave_radiation_sum": [4.17],
            "et0_fao_evapotranspiration": [0.092],
        },
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_current_weather_success(mock_current_weather_payload):
    """Verify current and daily weather data are correctly parsed from a successful response."""
    lat, lon = 34.0901, -118.4065

    respx.get(OPEN_METEO_FORECAST_URL).respond(
        status_code=200,
        json=mock_current_weather_payload,
    )

    async with httpx.AsyncClient() as client:
        result = await get_current_weather(latitude=lat, longitude=lon, client=client)

    # Current conditions
    assert result["current"]["temperature_2m"] == 72.5
    assert result["current"]["relative_humidity_2m"] == 45
    assert result["current"]["weather_code"] == 0
    assert result["current"]["wind_speed_10m"] == 8.4

    # Daily summary metrics
    assert result["daily"]["temperature_2m_max"][0] == 70.4
    assert result["daily"]["temperature_2m_min"][0] == 56.0
    assert result["daily"]["uv_index_max"][0] == 3.55
    assert result["daily"]["precipitation_probability_max"][0] == 45


@pytest.mark.asyncio
@respx.mock
async def test_get_current_weather_missing_keys():
    """Verify APIError is raised when response lacks required keys."""
    respx.get(OPEN_METEO_FORECAST_URL).respond(
        status_code=200,
        json={"latitude": 34.0901, "longitude": -118.4065},
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(APIError) as exc_info:
            await get_current_weather(
                latitude=34.0901, longitude=-118.4065, client=client
            )

    assert "missing 'current' or 'daily' weather data" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_get_current_weather_http_error():
    """Verify APIError is raised when the HTTP request returns a non-200 status."""
    respx.get(OPEN_METEO_FORECAST_URL).respond(
        status_code=500,
        text="Internal Server Error",
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(APIError):
            await get_current_weather(
                latitude=34.0901, longitude=-118.4065, client=client
            )
