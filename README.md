# Financial Analytics Platform

A modular stock analytics platform with separate layers for data acquisition, preprocessing, analytics, comparison, visualization, insights, and dashboard delivery.


<a href="https://your-dashboard.streamlit.app">
   Live Analytics Dashboard
</a>

## Project Structure

```text
stock-analytics-dashboard/
│
├── app.py
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── analytics.py
│   ├── comparison.py
│   ├── portfolio.py
│   ├── charts.py
│   └── insights.py
├── data/
│   ├── raw/
│   └── processed/
├── tests/
├── requirements.txt
└── README.md
```

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Layer

`src/data_loader.py` provides:
- `get_stock_data()`
- `save_stock_data()`
- `load_stock_data()`

Raw and processed files are stored under `data/raw` and `data/processed`.

## Test

```bash
python -m unittest discover -s tests -v
```
