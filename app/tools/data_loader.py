"""Load CSV / Excel files into pandas DataFrames."""

from pathlib import Path

import pandas as pd

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def load_dataset(file_path: str | Path) -> pd.DataFrame:
    """Read a CSV or Excel file and return a cleaned DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Please upload CSV or Excel."
        )

    if suffix == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    df = df.dropna(how="all")
    df.columns = [str(col).strip() for col in df.columns]
    return df


def dataset_summary(df: pd.DataFrame) -> dict:
    """Return a small summary so the agent understands the data."""
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numeric_columns": df.select_dtypes(include="number").columns.tolist(),
        "sample_rows": df.head(3).to_dict(orient="records"),
    }
