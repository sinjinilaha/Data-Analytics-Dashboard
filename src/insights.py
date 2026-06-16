from typing import List

import pandas as pd

from .analytics import calculate_drawdown, calculate_volatility


def generate_insights(df: pd.DataFrame) -> List[str]:
    insights = []
    if df.empty:
        return ["No data available for insight generation."]

    close = df["Close"].astype(float)
    if len(close) > 20:
        return_30d = ((close.iloc[-1] / close.iloc[-21]) - 1) * 100
        if return_30d > 10:
            insights.append("Stock gained more than 10% in the last month.")
        elif return_30d < -10:
            insights.append("Stock lost more than 10% in the last month.")

    volatility = calculate_volatility(df) * 100
    if volatility > 35:
        insights.append("Volatility is elevated, indicating higher risk.")
    else:
        insights.append("Volatility remains in a moderate range.")

    drawdown = calculate_drawdown(df)
    max_drawdown = drawdown.min() * 100
    insights.append(f"Maximum drawdown observed: {max_drawdown:.2f}%.")

    recent_volume = df["Volume"].tail(5).mean()
    avg_volume = df["Volume"].mean()
    if avg_volume > 0 and recent_volume > avg_volume:
        insights.append("Recent trading volume is above average.")

    return insights
