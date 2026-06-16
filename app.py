from datetime import date, timedelta

import streamlit as st

from src.analytics import calculate_volatility, daily_returns
from src.charts import (
    plot_comparison_chart,
    plot_price_chart,
    plot_return_chart,
    plot_volume_chart,
)
from src.comparison import compare_tickers
from src.data_loader import get_stock_data
from src.insights import generate_insights
from src.portfolio import portfolio_return, portfolio_volatility
from src.preprocessing import clean_stock_data


st.set_page_config(page_title="Financial Analytics Platform", layout="wide")
st.title("Financial Analytics Platform")

st.sidebar.header("Controls")
selected_tickers = st.sidebar.multiselect(
    "Stock Selection",
    options=["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"],
    default=["AAPL"],
)
start_date = st.sidebar.date_input("Start Date", value=date.today() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", value=date.today())

if selected_tickers and start_date < end_date:
    stock_data = {}
    for ticker in selected_tickers:
        raw_df = get_stock_data(ticker, start=start_date.isoformat(), end=end_date.isoformat())
        cleaned = clean_stock_data(raw_df)
        stock_data[ticker] = cleaned.set_index("Date")

    primary_ticker = selected_tickers[0]
    primary_df = stock_data[primary_ticker]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"{primary_df['Close'].iloc[-1]:.2f}")
    col2.metric("Return", f"{((primary_df['Close'].iloc[-1] / primary_df['Close'].iloc[0]) - 1) * 100:.2f}%")
    col3.metric("Volume", f"{primary_df['Volume'].iloc[-1]:,.0f}")
    col4.metric("Volatility", f"{calculate_volatility(primary_df) * 100:.2f}%")

    st.plotly_chart(plot_price_chart(primary_df), use_container_width=True)
    st.plotly_chart(plot_volume_chart(primary_df), use_container_width=True)

    returns = daily_returns(primary_df)
    st.plotly_chart(plot_return_chart(returns), use_container_width=True)

    st.subheader("Generated Insights")
    for line in generate_insights(primary_df):
        st.write(f"• {line}")

    if len(stock_data) > 1:
        comparison_df = compare_tickers(stock_data)
        st.subheader("Comparison Engine")
        st.dataframe(comparison_df)
        st.plotly_chart(plot_comparison_chart(comparison_df), use_container_width=True)

        st.subheader("Portfolio Simulator")
        equal_weights = {ticker: 1 / len(stock_data) for ticker in stock_data}
        st.metric("Expected Return", f"{portfolio_return(stock_data, equal_weights) * 100:.2f}%")
        st.metric("Portfolio Risk", f"{portfolio_volatility(stock_data, equal_weights) * 100:.2f}%")
else:
    st.info("Please select at least one stock and a valid date range.")
