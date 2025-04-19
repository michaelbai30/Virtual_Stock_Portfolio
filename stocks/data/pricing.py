import yfinance as yf
import pandas as pd

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period='1d', interval="5m", progress=False)

        if stock_data.empty:
            print(f"[Error] No data found for ticker '{ticker}'.")
            return None

        stock_data = stock_data[['Close']].copy()
        stock_data.columns = ['Price']
        stock_data.index = stock_data.index.strftime('%y-%m-%d %H:%M:%S')
        return stock_data.tail(12)

    except Exception as e:
        print(f"[Error] Failed to get stock data for '{ticker}'. Reason: {e}")
        return None

def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.fast_info.get("lastPrice")
        if price is None:
            raise ValueError("Price not available.")
        return round(price, 2)
    except Exception as e:
        print(f"[Error] Failed to retrieve price for '{ticker}'.")
        return None
