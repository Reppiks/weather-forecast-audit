import asyncio
import httpx
import streamlit as st
from clients.geocoding import get_coordinates_by_zip_code

# Configure page settings
st.set_page_config(
    page_title="Weather Forecast Audit",
    page_icon="🌤️",
    layout="wide",
)

col1, col2 = st.columns([0.8, 0.2])

with col1:
    st.title("Weather Analysis Dashboard")
    st.caption("Historical vs. Forecast Weather Data")


def run_async(coro):
    """Executes an async coroutine safely within Streamlit's thread environment."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


with col2:
    st.subheader("1. Enter Location")

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
            with st.spinner("Finding location details..."):
                try:
                    # Create a fresh client per request when executing via thread loop,
                    # or pass a clean call to run_async
                    async def fetch():
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            return await get_coordinates_by_zip_code(client, cleaned_zip)

                    location = run_async(fetch())

                    st.session_state["location"] = location

                    st.success(
                        f"Location: **{location['name']}, {location.get('admin1', '')}**"
                    )
                    aliased_json = {
                        "City": location["name"],
                        "State": location["admin1"],
                        "Country": location["country"],
                        "Latitude": location["latitude"],
                        "Longitude": location["longitude"],
                    }

                    st.table(aliased_json)

                except Exception as e:
                    st.error(f"Failed to look up ZIP code: {e}")
        else:
            st.warning("Please enter a valid 5-digit US ZIP code.")
