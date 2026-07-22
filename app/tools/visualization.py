"""Create Plotly charts from analysis results."""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Red theme shared with the Streamlit frontend
RED_SEQUENCE = ["#7f1d1d", "#b91c1c", "#dc2626", "#ef4444", "#f87171", "#fca5a5"]
RED_PRIMARY = "#dc2626"
RED_DARK = "#7f1d1d"


def chart_from_analysis(analysis: dict) -> dict | None:
    """Build a chart JSON payload based on which tool ran."""
    tool = analysis.get("tool")

    if tool in {"find_top_by_metric", "overview_plus_top"} and analysis.get("top_items"):
        items = analysis["top_items"]
        fig = px.bar(
            x=[i["name"] for i in items],
            y=[i["value"] for i in items],
            labels={"x": analysis.get("group_column", "Group"), "y": analysis.get("metric_column", "Value")},
            title="Top performers",
            color=[i["name"] for i in items],
            color_discrete_sequence=RED_SEQUENCE,
        )
        fig.update_layout(showlegend=False)
        return _fig_payload(fig, "bar")

    if tool in {"monthly_trend", "predict_next_month"} and (
        analysis.get("points") or analysis.get("history")
    ):
        points = analysis.get("points") or analysis.get("history") or []
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=[p["month"] for p in points],
                y=[p["value"] for p in points],
                mode="lines+markers",
                name="Actual",
                line={"color": RED_PRIMARY, "width": 3},
                marker={"color": RED_PRIMARY},
            )
        )
        if tool == "predict_next_month":
            fig.add_trace(
                go.Scatter(
                    x=[analysis["next_month"]],
                    y=[analysis["prediction"]],
                    mode="markers",
                    marker={"size": 14, "symbol": "star", "color": RED_DARK},
                    name="Forecast",
                )
            )
            fig.update_layout(title="Monthly trend + next-month forecast")
        else:
            fig.update_layout(title="Monthly sales trend")
        fig.update_layout(xaxis_title="Month", yaxis_title=analysis.get("metric_column", "Value"))
        return _fig_payload(fig, "line")

    return None


def _fig_payload(fig, chart_type: str) -> dict:
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        font={"color": "#7f1d1d"},
        title_font={"color": "#7f1d1d"},
    )
    fig.update_xaxes(gridcolor="#fecaca", zerolinecolor="#fca5a5")
    fig.update_yaxes(gridcolor="#fecaca", zerolinecolor="#fca5a5")
    return {
        "type": chart_type,
        "plotly_json": pio.to_json(fig),
    }
