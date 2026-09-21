import asyncio

import httpx
import pandas as pd

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


def process_comparison_data(actuals: dict, forecast: dict) -> pd.DataFrame:
    """Merges raw actuals and forecast JSON responses into a single pandas DataFrame."""
    try:
        actuals_hourly = actuals["hourly"]
        forecast_hourly = forecast["hourly"]
    except KeyError as exc:
        raise ValueError("Invalid weather payload: missing 'hourly' key.") from exc

    df_actuals = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(actuals_hourly["time"]),
            "temp_actual": actuals_hourly["temperature_2m"],
            "precip_actual": actuals_hourly["precipitation"],
        }
    )

    df_forecast = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(forecast_hourly["time"]),
            "temp_forecast": forecast_hourly["temperature_2m"],
            "precip_forecast": forecast_hourly["precipitation"],
        }
    )

    # Merge on timestamp to guarantee alignment
    merged_df = pd.merge(df_actuals, df_forecast, on="timestamp", how="inner")

    return merged_df
