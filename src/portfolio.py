from typing import Dict

import numpy as np
import pandas as pd

from .analytics import TRADING_DAYS, daily_returns


def _weights_to_series(weights: Dict[str, float]) -> pd.Series:
    series = pd.Series(weights, dtype=float)
    total = series.sum()
    if total <= 0:
        raise ValueError("Portfolio weights must sum to a positive value")
    return series / total


def portfolio_return(stock_data: Dict[str, pd.DataFrame], weights: Dict[str, float]) -> float:
    normalized = _weights_to_series(weights)
    returns = []
    for ticker, weight in normalized.items():
        if ticker in stock_data and not stock_data[ticker].empty:
            series = daily_returns(stock_data[ticker])
            if not series.empty:
                returns.append(series.rename(ticker) * weight)

    if not returns:
        return 0.0

    portfolio_daily = pd.concat(returns, axis=1).sum(axis=1)
    return float((1 + portfolio_daily).prod() - 1)


def portfolio_volatility(stock_data: Dict[str, pd.DataFrame], weights: Dict[str, float]) -> float:
    normalized = _weights_to_series(weights)

    return_series = []
    used_tickers = []
    for ticker in normalized.index:
        if ticker in stock_data and not stock_data[ticker].empty:
            series = daily_returns(stock_data[ticker])
            if not series.empty:
                return_series.append(series.rename(ticker))
                used_tickers.append(ticker)

    if not return_series:
        return 0.0

    matrix = pd.concat(return_series, axis=1).dropna()
    if matrix.empty:
        return 0.0

    weight_vector = normalized[used_tickers].to_numpy()
    cov = matrix.cov().to_numpy()
    variance = float(weight_vector.T @ cov @ weight_vector)
    return float(np.sqrt(variance) * np.sqrt(TRADING_DAYS))
