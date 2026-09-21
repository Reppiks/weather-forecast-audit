import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """Generates a dual-axis Plotly figure comparing actual vs. forecast temperature and precipitation."""
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
        subplot_titles=("7-Day Historical Variance: Actual vs. Forecast",),
    )

    # 1. Temperature Lines (Primary Y-Axis)
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["temp_actual"],
            name="Temp Actual (°F)",
            mode="lines",
            line={"color": "#EF553B", "width": 2.5},
            hovertemplate="%{x|%b %d, %I:%M %p}<br>Actual Temp: %{y:.1f}°F<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["temp_forecast"],
            name="Temp Forecast (°F)",
            mode="lines",
            line={"color": "#FFA15A", "width": 2, "dash": "dash"},
            hovertemplate="%{x|%b %d, %I:%M %p}<br>Forecast Temp: %{y:.1f}°F<extra></extra>",
        ),
        secondary_y=False,
    )

    # 2. Precipitation Bars (Secondary Y-Axis)
    # Full dataset retained so 0.00 in appears explicitly in hover tooltips.
    # Overlay barmode allows actual and forecast bars to layer neatly over each other.
    fig.add_trace(
        go.Bar(
            x=df["timestamp"],
            y=df["precip_actual"],
            name="Precip Actual (in)",
            marker_color="#19D3F3",
            opacity=0.6,
            hovertemplate="%{x|%b %d, %I:%M %p}<br>Actual Precip: %{y:.2f} in<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Bar(
            x=df["timestamp"],
            y=df["precip_forecast"],
            name="Precip Forecast (in)",
            marker_color="#00CC96",
            opacity=0.4,
            hovertemplate="%{x|%b %d, %I:%M %p}<br>Forecast Precip: %{y:.2f} in<extra></extra>",
        ),
        secondary_y=True,
    )

    # 3. Layout Configuration
    fig.update_layout(
        template="plotly_white",
        height=520,
        margin={"l": 20, "r": 20, "t": 60, "b": 80},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.25,
            "xanchor": "center",
            "x": 0.5,
        },
        barmode="overlay",  # Overlays bars on top of each other for thin hourly slots
        hovermode="x unified",
    )

    # Axis Labels
    fig.update_yaxes(title_text="Temperature (°F)", secondary_y=False)
    fig.update_yaxes(title_text="Precipitation (in)", secondary_y=True, showgrid=False)
    fig.update_xaxes(title_text="Date / Time")

    return fig
