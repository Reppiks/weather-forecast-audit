"""Tests for clients/past_weather_comparison.py."""

import httpx
import pandas as pd
import pytest
import respx

from clients.past_weather_comparison import (
    BASE_URL,
    fetch_weather_comparison,
    process_comparison_data,
)


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
    respx.get(BASE_URL).respond(status_code=200, json=mock_actuals_payload)

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


"""Tests for data normalization helper in clients/past_weather_comparison.py."""


def test_process_comparison_data_success(mock_actuals_payload, mock_forecast_payload):
    """Verify raw JSON payloads are correctly merged into a clean pandas DataFrame."""
    df = process_comparison_data(mock_actuals_payload, mock_forecast_payload)

    # Check structure
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        "timestamp",
        "temp_actual",
        "precip_actual",
        "temp_forecast",
        "precip_forecast",
    ]

    # Check values and types
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert df["temp_actual"].tolist() == [70.0, 68.5]
    assert df["temp_forecast"].tolist() == [72.1, 69.8]
    assert df["precip_actual"].tolist() == [0.0, 0.0]
    assert df["precip_forecast"].tolist() == [0.0, 0.01]


def test_process_comparison_data_missing_hourly_key():
    """Verify ValueError is raised if a payload is missing the 'hourly' key."""
    invalid_actuals = {"latitude": 34.0901, "longitude": -118.4065}
    valid_forecast = {
        "hourly": {
            "time": ["2026-09-14T00:00"],
            "temperature_2m": [72.1],
            "precipitation": [0.0],
        }
    }

    with pytest.raises(
        ValueError, match="Invalid weather payload: missing 'hourly' key."
    ):
        process_comparison_data(invalid_actuals, valid_forecast)

    def test_process_comparison_data_missing_inner_fields():
        """Verify ValueError is raised if 'hourly' exists but lacks required keys."""
        invalid_actuals = {
            "hourly": {
                "time": ["2026-09-14T00:00"],
                # missing temperature_2m and precipitation
            }
        }
        valid_forecast = {
            "hourly": {
                "time": ["2026-09-14T00:00"],
                "temperature_2m": [72.1],
                "precipitation": [0.0],
            }
        }

        with pytest.raises(ValueError, match="missing 'hourly' key or required fields"):
            process_comparison_data(invalid_actuals, valid_forecast)
