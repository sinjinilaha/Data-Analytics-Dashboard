from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf


def get_stock_data(
    ticker: str,
    period: str = "2y",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch historical stock data for a ticker using yfinance."""
    stock = yf.Ticker(ticker)
    if start or end:
        df = stock.history(start=start, end=end)
    else:
        df = stock.history(period=period)
    df.index.name = "Date"
    return df


def save_stock_data(
    df: pd.DataFrame,
    ticker: str,
    processed: bool = False,
    base_dir: str = "data",
) -> Path:
    """Save stock data into the raw or processed data folder."""
    folder = Path(base_dir) / ("processed" if processed else "raw")
    folder.mkdir(parents=True, exist_ok=True)
    file_name = f"cleaned_{ticker}.csv" if processed else f"{ticker}.csv"
    output_path = folder / file_name
    df.to_csv(output_path)
    return output_path


def load_stock_data(
    ticker: str,
    processed: bool = False,
    base_dir: str = "data",
) -> pd.DataFrame:
    """Load stock data from local raw/processed storage."""
    file_name = f"cleaned_{ticker}.csv" if processed else f"{ticker}.csv"
    path = Path(base_dir) / ("processed" if processed else "raw") / file_name
    df = pd.read_csv(path, parse_dates=["Date"])
    return df.set_index("Date")
