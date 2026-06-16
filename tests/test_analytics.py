import unittest

import pandas as pd

from src.analytics import calculate_drawdown, calculate_volatility, cumulative_returns, daily_returns


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "Close": [100, 110, 105, 120],
                "Volume": [1000, 1200, 900, 1400],
            },
            index=pd.date_range("2024-01-01", periods=4, freq="D"),
        )

    def test_daily_and_cumulative_returns(self):
        dr = daily_returns(self.df)
        cr = cumulative_returns(self.df)

        self.assertAlmostEqual(dr.iloc[0], 0.10)
        self.assertAlmostEqual(cr.iloc[-1], 0.20)

    def test_volatility_non_negative(self):
        volatility = calculate_volatility(self.df)
        self.assertGreaterEqual(volatility, 0.0)

    def test_drawdown_contains_peak_drop(self):
        drawdown = calculate_drawdown(self.df)
        self.assertAlmostEqual(drawdown.min(), -0.0455, places=4)


if __name__ == "__main__":
    unittest.main()
