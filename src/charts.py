import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .analytics import ma20, ma50


def _x_axis(df: pd.DataFrame):
    if isinstance(df.index, pd.DatetimeIndex):
        return df.index
    if "Date" in df.columns:
        return pd.to_datetime(df["Date"])
    return list(range(len(df)))


def plot_price_chart(df: pd.DataFrame) -> go.Figure:
    x = _x_axis(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=df["Close"], mode="lines", name="Price"))
    fig.add_trace(go.Scatter(x=x, y=ma20(df), mode="lines", name="MA20"))
    fig.add_trace(go.Scatter(x=x, y=ma50(df), mode="lines", name="MA50"))
    fig.update_layout(title="Price Trend", xaxis_title="Date", yaxis_title="Price")
    return fig


def plot_return_chart(returns: pd.Series) -> go.Figure:
    fig = px.histogram(returns, nbins=40, title="Returns Distribution")
    fig.update_layout(xaxis_title="Daily Return", yaxis_title="Count")
    return fig


def plot_volume_chart(df: pd.DataFrame) -> go.Figure:
    x = _x_axis(df)
    fig = go.Figure(go.Bar(x=x, y=df["Volume"], name="Volume"))
    fig.update_layout(title="Volume Trend", xaxis_title="Date", yaxis_title="Volume")
    return fig


def plot_comparison_chart(comparison_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(comparison_df, x="Ticker", y="Volatility", title="Volatility Comparison")
    return fig
