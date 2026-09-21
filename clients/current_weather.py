from typing import Any

import httpx

from .base import APIError, make_request

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


async def get_current_weather(
    latitude: float,
    longitude: float,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Fetch current weather metrics for given geographic coordinates.

    Args:
        latitude: Geographic latitude of the location.
        longitude: Geographic longitude of the location.
        client: Optional shared httpx.AsyncClient instance.

    Returns:
        Dict containing current weather metrics (temperature, humidity,
        wind speed, precipitation, weather code, etc.).

    Raises:
        APIError: If the HTTP request fails or response format is invalid.
    """
    # Map API variables requested in current conditions
    current_variables = [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "is_day",
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        "cloud_cover",
        "pressure_msl",
        "surface_pressure",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
    ]

    daily_variables = [
        "sunrise",
        "sunset",
        "moonrise",
        "moonset",
        "moon_phase",
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_min",
        "apparent_temperature_max",
        "uv_index_max",
        "uv_index_clear_sky_max",
        "daylight_duration",
        "sunshine_duration",
        "rain_sum",
        "showers_sum",
        "snowfall_sum",
        "precipitation_sum",
        "precipitation_hours",
        "precipitation_probability_max",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "wind_direction_10m_dominant",
        "shortwave_radiation_sum",
        "et0_fao_evapotranspiration",
    ]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(current_variables),
        "daily": ",".join(daily_variables),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "forecast_days": 1,
    }

    data = await make_request(
        client=client,
        url=OPEN_METEO_FORECAST_URL,
        params=params,
    )

    if "current" not in data or "daily" not in data:
        raise APIError(
            "Malformed API response: missing 'current' or 'daily' weather data.")

    return {
        "current": data["current"],
        "daily": data["daily"],
    }
