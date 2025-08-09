import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd
import datetime

def calculate_RSI(prices, period=14):
    if len(prices) < period + 1:
        return []

    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [max(d, 0) for d in deltas]
    losses = [abs(min(d, 0)) for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi = [None] * (period + 1) # padded for alignment with original price index

    for i in range(period, len(deltas)):
        gain = gains[i]
        loss = losses[i]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss != 0:
            rs = avg_gain / avg_loss
        else:
            rs = float('inf')
        rsi.append(100 - (100 / (1 + rs)))

    return rsi

def plot_stock_price(ticker, period, save_path=None):
    period_map = {
        '1d': {'plot_period': '1d', 'interval': '5m', 'fetch_period': '5d'},
        '1w': {'plot_period': '7d', 'interval': '30m', 'fetch_period': '10d'},
        '1m': {'plot_period': '30D', 'interval': '4h', 'fetch_period': '300d'},
        '3m': {'plot_period': '90D', 'interval': '1d', 'fetch_period': '400d'},
        '1y': {'plot_period': '365D', 'interval': '1d', 'fetch_period': '2y'},
        '5y': {'plot_period': '1825D', 'interval': '1wk', 'fetch_period': '10y'},
    }

    if period not in period_map:
        print(f"Invalid period '{period}'. Choose from {list(period_map.keys())}.")
        return

    settings = period_map[period]
    fetch_period = settings['fetch_period']
    interval = settings['interval']
    plot_period = settings['plot_period']

    stock = yf.Ticker(ticker)

    try:
        info = stock.info
        if not info or info.get('regularMarketPrice') is None:
            raise ValueError
    except Exception:
        print(f"Invalid ticker '{ticker.upper()}'.")
        return

    # fetch more data to support MA data
    full_data = stock.history(period=fetch_period, interval=interval)
    if full_data.empty:
        print(f"No data found for {ticker.upper()} with period '{period}'.")
        return

    full_data.index = full_data.index.tz_localize(None)
    display_data = full_data.last(plot_period)

    # calculate MA from the full dataset
    full_data['MA10'] = full_data['Close'].rolling(window=10).mean()
    full_data['MA50'] = full_data['Close'].rolling(window=50).mean()
    full_data['MA200'] = full_data['Close'].rolling(window=200).mean()

    # slice for the period to be displayed
    ma10 = full_data.loc[display_data.index, 'MA10']
    ma50 = full_data.loc[display_data.index, 'MA50']
    ma200 = full_data.loc[display_data.index, 'MA200']
    
    # rsi 
    rsi_vals = calculate_RSI(full_data['Close'].tolist(), period=14)
    full_data['RSI'] = rsi_vals
    rsi = full_data.loc[display_data.index, 'RSI']

    # plot subplot
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.15,
        subplot_titles=(f"{ticker.upper()} Prices", "RSI (14)")
    )

    # plot candlestick
    fig.add_trace(go.Candlestick(
        x=display_data.index,
        open=display_data['Open'],
        high=display_data['High'],
        low=display_data['Low'],
        close=display_data['Close'],
        name='Price'
    ), row=1, col=1)

    # plot MA
    fig.add_trace(go.Scatter(x=display_data.index, y=ma10, name='MA10', line=dict(color='yellow')), row=1, col=1)
    fig.add_trace(go.Scatter(x=display_data.index, y=ma50, name='MA50', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=display_data.index, y=ma200, name='MA200', line=dict(color='red')), row=1, col=1)

    # plot RSI
    fig.add_trace(go.Scatter(
        x=display_data.index,
        y=rsi,
        name='RSI(14)',
        line=dict(color='orange')
    ), row=2, col=1)

    fig.update_layout(
        title=f'{ticker.upper()} Price Over {period.upper()}',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_dark',
        hovermode='x unified',
        width=1000,
        height=500,
        xaxis_rangeslider_visible=False,
        showlegend=True
    )
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])

    if save_path:
        fig.write_html(save_path)
    else:
        fig.show()

def handle_plot_stock_price():
    ticker = input("Enter the ticker of the stock you wish to view (or N to cancel): ").upper()
    if ticker == "N":
        return

    valid_periods = ['1d', '1w', '1m', '3m', '1y', '5y']

    while True:
        period = input("Enter the period of time 1d, 1w, 1m, 3m, 1y, 5y (or N to cancel): ").lower()
        if period == "n":
            return
        if period in valid_periods:
            break
        print("Invalid period. Please enter one of: 1d, 1w, 1m, 3m, 1y, 5y, or N to cancel.")

    plot_stock_price(ticker, period)