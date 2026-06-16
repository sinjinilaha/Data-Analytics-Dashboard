import numpy as np
import pandas as pd

STANDARD_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize stock data and handle duplicates/missing values.

    Rows are dropped if price fields remain missing after forward/backward fill.
    """
    working = df.copy()

    if "Date" not in working.columns:
        working = working.reset_index()
        if "index" in working.columns:
            working = working.rename(columns={"index": "Date"})

    working["Date"] = pd.to_datetime(working["Date"])
    working = working.sort_values("Date").drop_duplicates(subset=["Date"])

    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in working.columns:
            working[col] = np.nan

    working = working[["Date", *required]].set_index("Date")

    if not working.empty:
        full_range = pd.date_range(working.index.min(), working.index.max(), freq="B")
        working = working.reindex(full_range)

    price_cols = ["Open", "High", "Low", "Close"]
    working[price_cols] = working[price_cols].ffill().bfill()
    working = working.dropna(subset=price_cols, how="any")
    working["Volume"] = working["Volume"].fillna(0)

    working.index.name = "Date"
    cleaned = working.reset_index()[STANDARD_COLUMNS]
    return cleaned
