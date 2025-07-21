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

def get_portfolio_summary():
    data = []
    total_value = portfolio.portfolio_value()
    cash_balance = portfolio.cash_balance

    for ticker, (shares, avg_price) in portfolio.holdings.items():
        cur_price = get_price(ticker)
        cur_val = round(cur_price * shares, 2)
        profit_loss = round((cur_price - avg_price) * shares, 2)
        profit_loss_percent = round ((profit_loss / (avg_price * shares)) * 100, 2) if avg_price > 0 else 0
        allocation_percent = round((cur_val / total_value) * 100, 2) if total_value > 0 else 0

        data.append({
        "ticker":ticker,
        "shares":shares,
        "current_value": cur_val,
        "profit_loss" : profit_loss,
        "profit_loss_percent" : profit_loss_percent,
        "allocation_percent" : allocation_percent
        })

    return {
        "total_value" : round(total_value, 2),
        "cash_balance" : round(cash_balance, 2),
        "allocations" : data
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

def generate_stock_chart(symbol: str, period: str, outpath: str) -> str:
    # create folder if doesn't exist
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    
    # generate and save chart
    plot_stock_price(symbol, period, save_path=outpath)

    return "/static/chart.html"