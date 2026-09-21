import pandas as pd
import plotly.graph_objects as go
import pytest

from components.comparison_chart import create_comparison_chart


@pytest.fixture
def sample_normalized_df():
    """Provides a sample normalized weather DataFrame."""
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2026-09-20 00:00:00", "2026-09-20 01:00:00"]),
            "temp_actual": [70.0, 68.5],
            "precip_actual": [0.0, 0.05],
            "temp_forecast": [71.5, 69.0],
            "precip_forecast": [0.0, 0.02],
        }
    )


def test_create_comparison_chart_returns_figure(sample_normalized_df):
    """Verify function creates a Plotly Figure instance."""
    fig = create_comparison_chart(sample_normalized_df)
    assert isinstance(fig, go.Figure)


def test_create_comparison_chart_trace_count_and_types(sample_normalized_df):
    """Verify figure contains 4 traces (2 Scatter lines, 2 Bar traces)."""
    fig = create_comparison_chart(sample_normalized_df)

    assert len(fig.data) == 4

    trace_names = [trace.name for trace in fig.data]
    assert "Temp Actual (°F)" in trace_names
    assert "Temp Forecast (°F)" in trace_names
    assert "Precip Actual (in)" in trace_names
    assert "Precip Forecast (in)" in trace_names

    # Verify trace visual types
    assert isinstance(fig.data[0], go.Scatter)
    assert isinstance(fig.data[1], go.Scatter)
    assert isinstance(fig.data[2], go.Bar)
    assert isinstance(fig.data[3], go.Bar)


def test_create_comparison_chart_secondary_y_axis(sample_normalized_df):
    """Verify precipitation bars are mapped to secondary y-axis."""
    fig = create_comparison_chart(sample_normalized_df)

    # In Plotly subplots, yaxis='y2' indicates secondary axis mapping
    assert fig.data[0].yaxis is None or fig.data[0].yaxis == "y"
    assert fig.data[1].yaxis is None or fig.data[1].yaxis == "y"
    assert fig.data[2].yaxis == "y2"
    assert fig.data[3].yaxis == "y2"
