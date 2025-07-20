# wrap core operations from the cli_src folder 
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cli_src')))

from portfolio.portfolio import Portfolio
from data.pricing import get_price
from data.plotting import plot_stock_price

portfolio_file = "portfolio.txt"
portfolio = Portfolio.load_file(portfolio_file)

def get_portfolio_data():
    return {
        "cash_balance" : portfolio.cash_balance,
        "portfolio_value" : portfolio.portfolio_value(),
        "holdings" : portfolio.holdings,
        "transactions": portfolio.transactions,
        "limit_orders": portfolio.limit_orders
    }

def buy_stock(symbol: str, shares: int):
    price = get_price(symbol)
    if price is None:
        return {"error": f"Ticker {symbol} not found."} # returns an http response body in JSON

    cost = price * shares
    if portfolio.cash_balance < cost:
        return {"error": f"Insufficient funds to buy {shares} of {symbol}."}

    portfolio.buy_stock(symbol, shares)
    portfolio.save_file(portfolio_file)
    return {"message": f"Bought {shares} shares of {symbol}", "price": price}


def sell_stock(symbol: str, shares: int):
    price = get_price(symbol)
    if price is None:
        return {"error": f"Ticker {symbol} not found."}

    if symbol not in portfolio.holdings or portfolio.holdings[symbol][0] < shares:
        return {"error": f"Insufficient shares to sell {shares} of {symbol}."}

    portfolio.sell_stock(symbol, shares)
    portfolio.save_file(portfolio_file)
    return {"message": f"Sold {shares} shares of {symbol}", "price": price}


def add_limit_order(symbol: str, shares: int, price: float, order_type: str):
    portfolio.queue_limit_order(symbol, shares, price, order_type)
    portfolio.save_file(portfolio_file)
    return {"message": f"Queued {shares} shares of {symbol} for {order_type} at ${price}"}

def run_limit_checks():
    tickers = set(order["ticker"] for order in portfolio.limit_orders)
    for ticker in tickers:
        portfolio.query_limit_buy_sell(ticker)
    portfolio.save_file(portfolio_file)

def get_price_json(symbol: str):
    price = get_price(symbol)
    if price is None:
        return {"error": "Invalid symbol or price not available."}
    return {"symbol": symbol, "price": price}