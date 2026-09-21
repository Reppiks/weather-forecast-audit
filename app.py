import asyncio
import pprint
from datetime import datetime

import httpx
import streamlit as st

from clients.base import APIError
from clients.current_weather import get_current_weather
from clients.geocoding import get_coordinates_by_zip_code
from clients.past_weather_comparison import (
    fetch_weather_comparison,
    process_comparison_data,
)
from components.comparison_chart import create_comparison_chart
from components.moon_component import render_moon_badge
from components.weather_code_component import render_weather_badge

# Configure page settings
st.set_page_config(
    page_title="Weather Forecast Audit",
    page_icon="🌤️",
    layout="wide",
)


def run_async(coro):
    """Executes an async coroutine safely within Streamlit's thread environment."""
    return asyncio.run(coro)


async def fetch_location_and_weather(zip_code: str):
    """Executes both API calls using a single httpx client session."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        location = await get_coordinates_by_zip_code(client, zip_code)
        today_metrics = await get_current_weather(
            latitude=location.get("latitude", "?"),
            longitude=location.get("longitude", "?"),
            client=client,
        )
        return location, today_metrics


async def fetch_comparison_data(lat: float, lon: float):
    """Asynchronously fetches past weather comparison data using httpx."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        return await fetch_weather_comparison(client, lat, lon)


def safe_first(data: dict, key: str, default=None):
    """Safely extracts the first element if the value is a list or tuple.

    Prevents IndexErrors and TypeErrors if the API returns an empty list or
    None.
    """
    if not isinstance(data, dict):
        return default

    val = data.get(key)
    if isinstance(val, (list, tuple)):
        return val[0] if len(val) > 0 else default
    return val if val is not None else default


def format_time(iso_str: str) -> str:
    """Converts an ISO timestamp (e.g., '2026-09-21T06:45') to 12-hour time ('6:45 AM')."""
    if not iso_str or not isinstance(iso_str, str):
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%I:%M %p").lstrip("0")
    except ValueError, TypeError:
        return "N/A"


# --- TOP LEVEL LAYOUT ---
col1, col2 = st.columns([0.65, 0.35])

with col1:
    st.title("Weather Analysis Dashboard")
    st.caption("Historical vs. Forecast Weather Data")

    # Only show historical chart if location is in session state
    if "location" in st.session_state:
        active_location = st.session_state["location"]
        target_lat = safe_first(active_location, "latitude")
        target_lon = safe_first(active_location, "longitude")

        if target_lat is not None and target_lon is not None:
            try:
                with st.spinner("Loading historical comparison chart..."):
                    actuals, forecast = run_async(
                        fetch_comparison_data(target_lat, target_lon)
                    )

                    df = process_comparison_data(actuals, forecast)

                    # Render Plotly Chart
                    fig = create_comparison_chart(df)
                    st.plotly_chart(fig, width="stretch")

            except (httpx.HTTPError, APIError, ValueError) as exc:
                st.error(f"Failed to fetch historical comparison data: {exc}")
    else:
        st.info(
            "Please enter a US ZIP code on the right to view historical forecast accuracy analysis."
        )

with col2:
    st.subheader("Enter Location")

    with st.form(key="location_form"):
        zip_code = st.text_input(
            label="US ZIP Code",
            max_chars=5,
            placeholder="e.g., 90210",
            help="Enter a 5-digit US ZIP code to fetch location coordinates.",
        )
        submitted = st.form_submit_button("Look Up Location", type="primary")

    if submitted:
        cleaned_zip = zip_code.strip()

        if len(cleaned_zip) == 5 and cleaned_zip.isdigit():
            with st.spinner("Fetching location & current weather..."):
                try:
                    location, today_conditions = run_async(
                        fetch_location_and_weather(cleaned_zip)
                    )

                    # Inspect API data in terminal
                    print("\n--- DEBUG: Location Data ---")
                    pprint.pprint(location)
                    print("--- DEBUG: Weather Data ---")
                    pprint.pprint(today_conditions)
                    print("----------------------------\n")

                    # Store results in session state
                    st.session_state["location"] = location
                    st.session_state["weather"] = today_conditions
                    st.rerun()

                except (APIError, ValueError) as e:
                    st.error(f"Failed to look up location or weather: {e}")
        else:
            st.warning("Please enter a valid 5-digit US ZIP code.")

    # --- RENDER RESULTS IN COLUMN 2 ---
    if "location" in st.session_state and "weather" in st.session_state:
        location = st.session_state.get("location", {})
        current_conditions = st.session_state["weather"].get("current", {})
        day_conditions = st.session_state["weather"].get("daily", {})

        # Normalize Location Display
        city = safe_first(location, "name", default="Unknown")
        state = safe_first(location, "admin1", default="")
        lat = safe_first(location, "latitude", default="?")
        lon = safe_first(location, "longitude", default="?")
        location_display = f"{city}, {state}".strip(", ") if state else city

        st.success(f"Location: **{location_display}**")
        st.caption(f"Lat: {lat} | Lon: {lon}")

        # Split col2 internally into two equal sub-columns
        sub_col1, sub_col2 = st.columns(2)

        # SUB-COLUMN 1: CURRENT CONDITIONS
        with sub_col1:
            st.markdown(body="#### Right Now", text_alignment="center")

            temp = safe_first(current_conditions, "temperature_2m")
            apparent_temp = safe_first(current_conditions, "apparent_temperature")
            humidity = safe_first(current_conditions, "relative_humidity_2m")
            wind = safe_first(current_conditions, "wind_speed_10m")

            current_conditions_table_data = {
                "Metric": ["Temp", "Feels Like", "Humidity", "Wind"],
                "Value": [
                    f"{round(temp)} °F" if temp is not None else "N/A",
                    f"{round(apparent_temp)} °F"
                    if apparent_temp is not None
                    else "N/A",
                    f"{round(humidity)} %" if humidity is not None else "N/A",
                    f"{round(wind, 1)} mph" if wind is not None else "N/A",
                ],
            }
            st.dataframe(
                current_conditions_table_data,
                hide_index=True,
                width="stretch",
            )

            weather_code = safe_first(day_conditions, "weather_code", default=0)
            render_weather_badge(
                weather_code=weather_code,
                title="CURRENT",
                size="small",
                full_width=True,
            )

        # SUB-COLUMN 2: TODAY'S DAILY FORECAST
        with sub_col2:
            st.markdown(body="#### Today's Summary", text_alignment="center")

            high_temp = safe_first(day_conditions, "temperature_2m_max", default=0)
            low_temp = safe_first(day_conditions, "temperature_2m_min", default=0)
            sunrise_raw = safe_first(day_conditions, "sunrise", default="")
            sunset_raw = safe_first(day_conditions, "sunset", default="")
            moonrise_raw = safe_first(day_conditions, "moonrise", default="")

            day_conditions_table_data = {
                "Metric": [
                    "High / Low",
                    "Sunrise",
                    "Sunset",
                    "Moonrise",
                ],
                "Value": [
                    f"{round(high_temp)}° / {round(low_temp)}°F",
                    format_time(sunrise_raw),
                    format_time(sunset_raw),
                    format_time(moonrise_raw),
                ],
            }
            st.dataframe(
                day_conditions_table_data,
                hide_index=True,
                width="stretch",
            )

            moon_phase_value = safe_first(day_conditions, "moon_phase", default=0.25)
            render_moon_badge(
                moon_phase_value=moon_phase_value,
                title="MOONPHASE",
                size="small",
                full_width=True,
            )
