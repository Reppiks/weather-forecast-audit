import streamlit as st

WMO_CODE_MAP = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌧️"),
    53: ("Moderate Drizzle", "🌧️"),
    55: ("Dense Drizzle", "🌧️"),
    56: ("Freezing Drizzle", "🌧️❄️"),
    57: ("Dense Freezing Drizzle", "🌧️❄️"),
    61: ("Slight Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    66: ("Freezing Rain", "🌧️❄️"),
    67: ("Heavy Freezing Rain", "🌧️❄️"),
    71: ("Slight Snow", "❄️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "❄️"),
    80: ("Slight Rain Showers", "🌦️"),
    81: ("Moderate Rain Showers", "🌦️"),
    82: ("Violent Rain Showers", "🌧️"),
    85: ("Slight Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "🌨️"),
    95: ("Thunderstorm", "🌩️"),
    96: ("Thunderstorm w/ Hail", "🌩️🧊"),
    99: ("Severe Thunderstorm w/ Hail", "🌩️🧊"),
}


def _normalize_code(weather_code) -> int:
    if isinstance(weather_code, (list, tuple)):
        weather_code = weather_code[0] if len(weather_code) > 0 else 0
    if weather_code is None:
        return 0
    try:
        return int(weather_code)
    except ValueError, TypeError:
        return 0


def get_weather_info(weather_code) -> tuple[str, str]:
    clean_code = _normalize_code(weather_code)
    return WMO_CODE_MAP.get(clean_code, (f"Condition Code {clean_code}", "🌡️"))


def render_weather_badge(
    weather_code, title: str = "TODAY", size: str = "large", full_width: bool = True
):
    label, emoji = get_weather_info(weather_code)

    size_settings = {
        "small": {
            "emoji_size": "28px",
            "title_size": "11px",
            "label_size": "14px",
            "padding": "12px 16px",
            "gap": "12px",
        },
        "medium": {
            "emoji_size": "42px",
            "title_size": "12px",
            "label_size": "18px",
            "padding": "16px 20px",
            "gap": "16px",
        },
        "large": {
            "emoji_size": "52px",
            "title_size": "13px",
            "label_size": "22px",
            "padding": "18px 24px",
            "gap": "20px",
        },
    }

    cfg = size_settings.get(size, size_settings["large"])

    display_type = "flex" if full_width else "inline-flex"
    width_style = "width: 100%; box-sizing: border-box;" if full_width else ""

    st.markdown(
        f"""
        <div style="
            display: {display_type};
            {width_style}
            align-items: center;
            gap: {cfg["gap"]};
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: {cfg["padding"]};
            color: #e6edf3;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-sizing: border-box;
        ">
            <span style="font-size: {cfg["emoji_size"]}; flex-shrink: 0; line-height: 1;">{emoji}</span>
            <div style="flex-grow: 1;">
                <div style="font-size: {cfg["title_size"]}; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">{title}</div>
                <div style="font-size: {cfg["label_size"]}; font-weight: 700; line-height: 1.2;">{label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
