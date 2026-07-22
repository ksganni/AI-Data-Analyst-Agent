from pathlib import Path

import pytest

from app.tools.analytics import find_top_by_metric, monthly_trend, predict_next_month, run_analysis
from app.tools.data_loader import load_dataset

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SAMPLE = DATA_DIR / "sample_sales.csv"


def test_load_sample_dataset():
    df = load_dataset(SAMPLE)
    assert len(df) > 0
    assert "revenue" in df.columns


@pytest.mark.parametrize(
    "filename",
    [
        "sample_sales.csv",
        "sample_marketing.csv",
        "sample_customer_orders.csv",
        "sample_inventory.csv",
    ],
)
def test_all_sample_datasets_support_analysis(filename):
    df = load_dataset(DATA_DIR / filename)
    top_result = run_analysis(df, "Which group generated the highest revenue?")
    trend_result = run_analysis(df, "Show the monthly revenue trend.")

    assert top_result["tool"] == "find_top_by_metric"
    assert top_result["top_items"]
    assert trend_result["tool"] == "monthly_trend"
    assert trend_result["points"]


def test_highest_revenue_product():
    df = load_dataset(SAMPLE)
    result = find_top_by_metric(df)
    assert result["top_items"][0]["name"] == "Widget C"
    assert "highest" in result["answer"].lower()


def test_monthly_trend():
    df = load_dataset(SAMPLE)
    result = monthly_trend(df)
    assert len(result["points"]) >= 2
    assert result["points"][0]["month"].startswith("2025-")


def test_predict_next_month():
    df = load_dataset(SAMPLE)
    result = predict_next_month(df)
    assert result["prediction"] > 0
    assert result["next_month"].startswith("2025-")


def test_run_analysis_routes_questions():
    df = load_dataset(SAMPLE)
    assert run_analysis(df, "Which product generated the highest revenue?")["tool"] == "find_top_by_metric"
    assert run_analysis(df, "Show monthly sales trends.")["tool"] == "monthly_trend"
    assert run_analysis(df, "Predict next month's sales.")["tool"] == "predict_next_month"
