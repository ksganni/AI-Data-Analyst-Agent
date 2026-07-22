"""Business analytics helpers built with pandas / numpy."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd


def _pick_column(df: pd.DataFrame, candidates: list[str], fallback_numeric: bool = False) -> str | None:
    lower_map = {col.lower(): col for col in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]

    for col in df.columns:
        col_l = col.lower()
        if any(name.lower() in col_l for name in candidates):
            return col

    if fallback_numeric:
        numeric = df.select_dtypes(include="number").columns.tolist()
        return numeric[0] if numeric else None
    return None


def find_top_by_metric(
    df: pd.DataFrame,
    group_col: str | None = None,
    metric_col: str | None = None,
    top_n: int = 5,
) -> dict:
    """Find groups with the highest metric total (e.g. product revenue)."""
    group_col = group_col or _pick_column(
        df,
        [
            "product",
            "category",
            "campaign",
            "channel",
            "item",
            "region",
            "customer",
            "name",
        ],
    )
    metric_col = metric_col or _pick_column(
        df, ["revenue", "sales", "amount", "total", "price"], fallback_numeric=True
    )

    if not group_col or not metric_col:
        raise ValueError("Could not find group and metric columns in the dataset.")

    ranked = (
        df.groupby(group_col, dropna=False)[metric_col]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )
    winner = ranked.index[0]
    return {
        "group_column": group_col,
        "metric_column": metric_col,
        "top_items": [
            {"name": str(idx), "value": float(val)} for idx, val in ranked.items()
        ],
        "answer": f"'{winner}' generated the highest {metric_col}: {float(ranked.iloc[0]):,.2f}",
    }


def monthly_trend(
    df: pd.DataFrame,
    date_col: str | None = None,
    metric_col: str | None = None,
) -> dict:
    """Aggregate a metric by month."""
    date_col = date_col or _pick_column(df, ["date", "order_date", "month", "timestamp"])
    metric_col = metric_col or _pick_column(
        df, ["revenue", "sales", "amount", "total"], fallback_numeric=True
    )
    if not date_col or not metric_col:
        raise ValueError("Need a date column and a numeric metric column.")

    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work = work.dropna(subset=[date_col])
    work["month"] = work[date_col].dt.to_period("M").astype(str)
    trend = work.groupby("month")[metric_col].sum().reset_index()
    trend = trend.sort_values("month")

    return {
        "date_column": date_col,
        "metric_column": metric_col,
        "points": [
            {"month": row["month"], "value": float(row[metric_col])}
            for _, row in trend.iterrows()
        ],
        "answer": (
            f"Monthly {metric_col} ranges from "
            f"{float(trend[metric_col].min()):,.2f} to "
            f"{float(trend[metric_col].max()):,.2f}."
        ),
    }


def describe_numeric(df: pd.DataFrame) -> dict:
    """Basic descriptive stats for numeric columns."""
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return {"answer": "No numeric columns found.", "stats": {}}

    stats = numeric.describe().round(2).to_dict()
    return {
        "stats": stats,
        "answer": f"Computed descriptive statistics for {len(numeric.columns)} numeric columns.",
    }


def predict_next_month(
    df: pd.DataFrame,
    date_col: str | None = None,
    metric_col: str | None = None,
) -> dict:
    """Simple next-month forecast using linear trend on monthly totals."""
    trend = monthly_trend(df, date_col=date_col, metric_col=metric_col)
    values = np.array([p["value"] for p in trend["points"]], dtype=float)
    if len(values) < 2:
        raise ValueError("Need at least 2 months of data to forecast.")

    x = np.arange(len(values))
    slope, intercept = np.polyfit(x, values, 1)
    prediction = float(slope * len(values) + intercept)
    last_month = trend["points"][-1]["month"]
    year, month = map(int, last_month.split("-"))
    if month == 12:
        next_month = f"{year + 1}-01"
    else:
        next_month = f"{year}-{month + 1:02d}"

    return {
        "metric_column": trend["metric_column"],
        "history": trend["points"],
        "next_month": next_month,
        "prediction": round(prediction, 2),
        "method": "linear_trend",
        "answer": (
            f"Predicted {trend['metric_column']} for {next_month} is "
            f"{prediction:,.2f} (simple linear trend)."
        ),
    }


def run_analysis(df: pd.DataFrame, question: str) -> dict:
    """Pick a simple analysis path from the user's question."""
    q = question.lower().strip()

    if re.search(r"predict|forecast|next month", q):
        result = predict_next_month(df)
        result["tool"] = "predict_next_month"
        return result

    if re.search(r"trend|monthly|over time|time series", q):
        result = monthly_trend(df)
        result["tool"] = "monthly_trend"
        return result

    if re.search(r"highest|top|best|most|rank", q):
        result = find_top_by_metric(df)
        result["tool"] = "find_top_by_metric"
        return result

    if re.search(r"summary|describe|overview|average|mean", q):
        result = describe_numeric(df)
        result["tool"] = "describe_numeric"
        return result

    # Default: give a useful overview + top metric if possible
    overview = describe_numeric(df)
    try:
        top = find_top_by_metric(df)
        overview["top_items"] = top["top_items"]
        overview["answer"] = (
            f"{overview['answer']} {top['answer']}"
        )
        overview["tool"] = "overview_plus_top"
    except ValueError:
        overview["tool"] = "describe_numeric"
    return overview
