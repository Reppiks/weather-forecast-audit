import base64
import math

import streamlit as st

PHASE_NAMES = [
    (0.00, 0.00, "New Moon"),
    (0.00, 0.25, "Waxing Crescent"),
    (0.25, 0.25, "First Quarter"),
    (0.25, 0.50, "Waxing Gibbous"),
    (0.50, 0.50, "Full Moon"),
    (0.50, 0.75, "Waning Gibbous"),
    (0.75, 0.75, "Last Quarter"),
    (0.75, 1.00, "Waning Crescent"),
]


def _normalize_phase(phase) -> float:
    """Safely converts input lists, ints, or floats into a valid float."""
    if isinstance(phase, (list, tuple)):
        phase = phase[0] if len(phase) > 0 else 0.0
    if phase is None:
        return 0.0
    try:
        return float(phase)
    except ValueError, TypeError:
        return 0.0


def get_phase_name(phase: float) -> str:
    clean_phase = round(_normalize_phase(phase), 2)
    if clean_phase in (0.0, 1.0):
        return "New Moon"
    for start, end, name in PHASE_NAMES:
        if start < clean_phase < end:
            return name
        if clean_phase == start:
            return name
    return "New Moon"


def _generate_moon_svg(phase: float, size: int) -> str:
    """Generates a crisp SVG string for the moon phase."""
    radius = (size // 2) - 2
    cx = size // 2
    cy = size // 2
    cos_p = math.cos(phase * 2 * math.pi)
    rx = abs(cos_p) * radius
    sweep = 1 if phase <= 0.5 else 0

    svg = f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="{cx}" cy="{cy}" r="{radius}" fill="#1c2128"/>
      <path d="M {cx} {cy - radius} A {radius} {radius} 0 0 {sweep} {cx} {cy + radius} A {rx} {radius} 0 0 {1 if cos_p < 0 else 0} {cx} {cy - radius}" fill="#f0f6fc"/>
    </svg>"""
    return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"


def render_moon_badge(
    moon_phase_value,
    title: str = "MOONPHASE",
    size: str = "large",
    full_width: bool = True,
):
    """Renders a styled moon phase badge matching the weather widget layout.

    Args:
        moon_phase_value: Moon phase float (0.0 to 1.0) or list containing float.
        title (str): Category header text (e.g., 'MOONPHASE' or 'TODAY').
        size (str): 'small', 'medium', or 'large'.
        full_width (bool): If True, stretches horizontally to fit the Streamlit column.
    """
    clean_phase = _normalize_phase(moon_phase_value)
    phase_name = get_phase_name(clean_phase)

    size_settings = {
        "small": {
            "icon_size": 28,
            "title_size": "11px",
            "label_size": "14px",
            "padding": "12px 16px",
            "gap": "12px",
        },
        "medium": {
            "icon_size": 42,
            "title_size": "12px",
            "label_size": "18px",
            "padding": "16px 20px",
            "gap": "16px",
        },
        "large": {
            "icon_size": 52,
            "title_size": "13px",
            "label_size": "22px",
            "padding": "18px 24px",
            "gap": "20px",
        },
    }

    cfg = size_settings.get(size, size_settings["large"])
    svg_data = _generate_moon_svg(clean_phase, cfg["icon_size"])

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
            <img src="{svg_data}" width="{cfg["icon_size"]}" height="{cfg["icon_size"]}" style="flex-shrink: 0; display: block;" />
            <div style="flex-grow: 1;">
                <div style="font-size: {cfg["title_size"]}; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">{title}</div>
                <div style="font-size: {cfg["label_size"]}; font-weight: 700; line-height: 1.2;">{phase_name}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
