import unittest

import pandas as pd

from src.comparison import compare_tickers


class TestComparison(unittest.TestCase):
    def test_compare_tickers_output_columns(self):
        dates = pd.date_range("2024-01-01", periods=3, freq="D")
        stock_data = {
            "AAPL": pd.DataFrame({"Close": [100, 110, 120], "Volume": [1000, 1100, 1200]}, index=dates),
            "MSFT": pd.DataFrame({"Close": [100, 102, 104], "Volume": [1500, 1400, 1450]}, index=dates),
        }

        result = compare_tickers(stock_data)

        self.assertEqual(list(result.columns), ["Ticker", "Return", "Volatility", "Volume"])
        self.assertEqual(result.iloc[0]["Ticker"], "AAPL")

    def test_compare_tickers_empty_inputs(self):
        result = compare_tickers({"AAPL": pd.DataFrame(), "MSFT": pd.DataFrame()})
        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main()
