from typing import List

import pandas as pd

from .analytics import calculate_drawdown, calculate_volatility

SIGNIFICANT_MOVE_THRESHOLD_PERCENT = 10
HIGH_VOLATILITY_THRESHOLD_PERCENT = 35


def generate_insights(df: pd.DataFrame) -> List[str]:
    insights = []
    if df.empty:
        return ["No data available for insight generation."]

    close = df["Close"].astype(float)
    if len(close) >= 21:
        # Use -21 to compare latest close to roughly one trading month ago (about 20 intervals).
        return_20d = ((close.iloc[-1] / close.iloc[-21]) - 1) * 100
        if return_20d > SIGNIFICANT_MOVE_THRESHOLD_PERCENT:
            insights.append(
                f"Stock gained more than {SIGNIFICANT_MOVE_THRESHOLD_PERCENT}% in the last month."
            )
        elif return_20d < -SIGNIFICANT_MOVE_THRESHOLD_PERCENT:
            insights.append(
                f"Stock lost more than {SIGNIFICANT_MOVE_THRESHOLD_PERCENT}% in the last month."
            )

    volatility = calculate_volatility(df) * 100
    if volatility > HIGH_VOLATILITY_THRESHOLD_PERCENT:
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
