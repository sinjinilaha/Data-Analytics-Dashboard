from typing import Dict

import pandas as pd

from .analytics import calculate_volatility


def compare_tickers(stock_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create comparison table with return, volatility, and average volume."""
    rows = []
    for ticker, df in stock_data.items():
        if df.empty:
            continue
        start_close = float(df["Close"].iloc[0])
        end_close = float(df["Close"].iloc[-1])
        total_return = (end_close / start_close) - 1 if start_close != 0 else float("nan")
        avg_volume = float(df["Volume"].mean()) if "Volume" in df.columns else 0.0
        rows.append(
            {
                "Ticker": ticker,
                "Return": total_return,
                "Volatility": calculate_volatility(df),
                "Volume": avg_volume,
            }
        )

    comparison = pd.DataFrame(rows)
    if comparison.empty:
        return comparison
    return comparison.sort_values("Return", ascending=False, na_position="last").reset_index(drop=True)
