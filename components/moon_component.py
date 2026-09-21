# moon_component.py
import streamlit.components.v1 as components

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
            "canvas_size": 32,
            "title_size": "11px",
            "label_size": "14px",
            "padding": "12px 16px",
            "gap": "12px",
            "height": 70,
        },
        "medium": {
            "canvas_size": 48,
            "title_size": "12px",
            "label_size": "18px",
            "padding": "16px 20px",
            "gap": "16px",
            "height": 95,
        },
        "large": {
            "canvas_size": 60,
            "title_size": "13px",
            "label_size": "22px",
            "padding": "18px 24px",
            "gap": "20px",
            "height": 115,
        },
    }

    cfg = size_settings.get(size, size_settings["large"])

    display_type = "flex" if full_width else "inline-flex"
    width_style = "width: 100%; box-sizing: border-box;" if full_width else ""

    canvas_size = cfg["canvas_size"]
    radius = (canvas_size // 2) - 2
    cx = canvas_size // 2
    cy = canvas_size // 2

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                overflow: hidden;
            }}
            .badge-container {{
                display: {display_type};
                {width_style}
                align-items: center;
                gap: {cfg["gap"]};
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
                padding: {cfg["padding"]};
                color: #e6edf3;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
        </style>
    </head>
    <body>
        <div class="badge-container">
            <canvas id="moonCanvas" width="{canvas_size}" height="{canvas_size}" style="flex-shrink: 0;"></canvas>
            <div style="flex-grow: 1;">
                <div style="font-size: {cfg["title_size"]}; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">{title}</div>
                <div style="font-size: {cfg["label_size"]}; font-weight: 700; line-height: 1.2;">{phase_name}</div>
            </div>
        </div>

        <script>
            (function() {{
                const canvas = document.getElementById('moonCanvas');
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                const phase = {clean_phase};
                const radius = {radius};
                const cx = {cx};
                const cy = {cy};

                // Base dark sphere
                ctx.beginPath();
                ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
                ctx.fillStyle = '#1c2128';
                ctx.fill();

                // Illuminated moon surface
                const cosPhase = Math.cos(phase * 2 * Math.PI);
                ctx.save();
                ctx.beginPath();
                ctx.arc(cx, cy, radius, -Math.PI / 2, Math.PI / 2, phase > 0.5);
                ctx.ellipse(cx, cy, Math.abs(cosPhase) * radius, radius, 0, Math.PI / 2, -Math.PI / 2, cosPhase < 0);
                
                ctx.shadowColor = 'rgba(240, 246, 252, 0.35)';
                ctx.shadowBlur = 8;
                ctx.fillStyle = '#f0f6fc';
                ctx.fill();
                ctx.restore();
            }})();
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=cfg["height"])
