import unittest

import pandas as pd

from src.preprocessing import clean_stock_data


class TestPreprocessing(unittest.TestCase):
    def test_clean_stock_data_handles_duplicates_and_nans(self):
        df = pd.DataFrame(
            {
                "Date": ["2024-01-01", "2024-01-01", "2024-01-03"],
                "Open": [100, 100, None],
                "High": [101, 101, 105],
                "Low": [99, 99, 100],
                "Close": [100, 100, 104],
                "Volume": [1000, 1000, None],
            }
        )

        cleaned = clean_stock_data(df)

        self.assertEqual(list(cleaned.columns), ["Date", "Open", "High", "Low", "Close", "Volume"])
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(cleaned["Date"].dt.strftime("%Y-%m-%d").tolist(), ["2024-01-01", "2024-01-02", "2024-01-03"])

        filled_middle = cleaned.iloc[1]
        self.assertEqual(filled_middle["Close"], 100)
        self.assertEqual(filled_middle["Volume"], 0)
        self.assertFalse(cleaned.isna().any().any())

    def test_clean_stock_data_empty_input(self):
        empty_df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        cleaned = clean_stock_data(empty_df)
        self.assertEqual(list(cleaned.columns), ["Date", "Open", "High", "Low", "Close", "Volume"])
        self.assertTrue(cleaned.empty)


if __name__ == "__main__":
    unittest.main()
