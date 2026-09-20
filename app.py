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

st.title("Weather Analysis Dashboard")
st.caption("Historical vs. Forecast Weather Data")


@st.cache_resource
def get_async_client() -> httpx.AsyncClient:
    """Creates a singleton httpx.AsyncClient cached across Streamlit reruns."""
    return httpx.AsyncClient(timeout=10.0)


# Instantiate/retrieve the shared client instance
client = get_async_client()

st.subheader("1. Enter Location")

# ZIP code Input Widget
zip_code = st.text_input(
    label="US ZIP Code",
    max_chars=5,
    placeholder="e.g., 90210",
    help="Enter a 5-digit US ZIP code to fetch location coordinates.",
)

if st.button("Look Up Location", type="primary"):
    if zip_code and len(zip_code) == 5 and zip_code.isdigit():
        with st.spinner("Finding location details..."):
            try:
                # call geocoding module using the shared cached client
                location = asyncio.run(
                    get_coordinates_by_zip_code(client, zip_code)
                )

                # Persist location in Streamlit session state for future weather calls
                st.session_state["location"] = location

                st.success(
                    f"Found location: **{location['name']}, {location.get('admin1', '')}**"
                )

                # Display raw location metadata
                st.json(location)

            except Exception as e:
                st.error(f"Failed to look up ZIP code: {e}")
            else:
                st.warning("Please enter a valid 5-digit US ZIP code.")
