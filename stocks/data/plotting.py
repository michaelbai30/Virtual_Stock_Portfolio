import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import datetime

def plot_stock_price(ticker, period):
    period_map = {
        '1d': ('1d', '5m'),
        '1w': ('5d', '30m'),
        '1m': ('1mo', '1d'),
        '3m': ('3mo', '1d'),
        '1y': ('1y', '1d'),
        '5y': ('5y', '1wk'),
    }
    if period not in period_map:
        raise ValueError("Invalid Period. Choose from 1d, 1w, 1m, 3m, 1y, 5y")
    
    yf_period, interval = period_map[period]
    stock = yf.Ticker(ticker)  
    
    try:
        info = stock.info
        if not info or info.get('regularMarketPrice') is None:
            raise ValueError
    except Exception:
        print(f"Invalid ticker '{ticker}'.")
        return


    stock_data = stock.history(period=yf_period, interval=interval)

    if stock_data.empty:
        print(f"No data found for {ticker} with period {period}")
        return

    stock_data.index = stock_data.index.tz_localize(None)
    
    fig = go.Figure(data=[go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'], high = stock_data['High'],
        close=stock_data['Close'], low = stock_data['Low'],
    )])

    fig.update_layout(
        title = f'{ticker} Price Over {period.upper()}',
        xaxis_title = 'Date',
        yaxis_title = 'Price ($)',
        template = 'plotly_dark',
        hovermode = 'x unified',
        width = 1200,
        height = 600
    )
    fig.show()


def handle_plot_stock_price():
    ticker = input("Enter the ticker of the stock you wish to view (or N to cancel): ").upper()
    if ticker == "N":
        return
    period = input("Enter the period of time 1d, 1w, 1m, 3m, 1y, 5y (or N to cancel): ").lower()
    if period == "N":
        return
    plot_stock_price(ticker, period)
    