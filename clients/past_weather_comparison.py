import asyncio
import httpx

BASE_URL = "https://api.open-meteo.com/v1/forecast"


async def fetch_weather_comparison(
    client: httpx.AsyncClient,
    latitude: float,
    longitude: float,
    past_days: int = 7,
) -> tuple[dict, dict]:
    """Fetches both Best-Match actuals and GEM model forecast data concurrently."""
    params_actuals = {
        "latitude": latitude,
        "longitude": longitude,
        "past_days": past_days,
        "forecast_days": 0,
        "hourly": "temperature_2m,precipitation",
        "temperature_unit": "fahrenheit",
    }

    params_forecast = {
        **params_actuals,
        "models": "gem_seamless",
    }

    # Fire both requests concurrently using asyncio.gather
    actuals_res, forecast_res = await asyncio.gather(
        client.get(BASE_URL, params=params_actuals),
        client.get(BASE_URL, params=params_forecast),
    )

    actuals_res.raise_for_status()
    forecast_res.raise_for_status()

    return actuals_res.json(), forecast_res.json()
