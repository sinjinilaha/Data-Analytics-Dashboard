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
        self.assertFalse(cleaned.isna().any().any())


if __name__ == "__main__":
    unittest.main()
