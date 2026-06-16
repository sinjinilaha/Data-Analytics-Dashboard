import numpy as np
import pandas as pd


TRADING_DAYS = 252


def _close_series(df: pd.DataFrame) -> pd.Series:
    if "Close" not in df.columns:
        raise ValueError("DataFrame must include a 'Close' column")
    return df["Close"].astype(float)


def daily_returns(df: pd.DataFrame) -> pd.Series:
    return _close_series(df).pct_change().dropna()


def monthly_returns(df: pd.DataFrame) -> pd.Series:
    close = _close_series(df)
    if isinstance(df.index, pd.DatetimeIndex):
        month_close = close.resample("M").last()
    elif "Date" in df.columns:
        month_close = pd.Series(close.values, index=pd.to_datetime(df["Date"])).resample("M").last()
    else:
        raise ValueError("DataFrame must have DatetimeIndex or Date column for monthly returns")
    return month_close.pct_change().dropna()


def cumulative_returns(df: pd.DataFrame) -> pd.Series:
    returns = daily_returns(df)
    return (1 + returns).cumprod() - 1


def ma20(df: pd.DataFrame) -> pd.Series:
    return _close_series(df).rolling(window=20).mean()


def ma50(df: pd.DataFrame) -> pd.Series:
    return _close_series(df).rolling(window=50).mean()


def ma200(df: pd.DataFrame) -> pd.Series:
    return _close_series(df).rolling(window=200).mean()


def calculate_volatility(df: pd.DataFrame) -> float:
    returns = daily_returns(df)
    if returns.empty:
        return 0.0
    return float(returns.std() * np.sqrt(TRADING_DAYS))


def calculate_drawdown(df: pd.DataFrame) -> pd.Series:
    close = _close_series(df)
    running_max = close.cummax()
    return (close / running_max) - 1
