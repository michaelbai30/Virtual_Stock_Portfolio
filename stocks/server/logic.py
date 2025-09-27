"""
server/logic.py

Wrapper around cli_src portfolio/data helpers for use by Flask API

Functions:
- Defines storage paths and and loads state.
- Exposes and defines logic for functions used by app.py routes
- Persists to disk and provides reload_portfolio()/reload_watchlist() so uploads
are reflected immediately.
"""
import sys
import os
import datetime
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cli_src')))
from portfolio.portfolio import Portfolio
from data.pricing import get_price
from data.plotting import plot_stock_price

# loads the saveed portfolio from disk
BASE_DIR = os.environ.get("STORAGE_ROOT", os.path.dirname(os.path.abspath(__file__)))
portfolio_file = os.path.join(BASE_DIR, "portfolio.txt")
watchlist_file = os.path.join(BASE_DIR, "watchlist.txt")
portfolio = Portfolio.load_file(portfolio_file)

portfolio_lock = threading.RLock()
def reload_portfolio():
    """Reload portfolio from disk into memory after an upload."""
    global portfolio
    with portfolio_lock:
        portfolio = Portfolio.load_file(portfolio_file)
    return portfolio

# return current portfolio state in json, from the loaded portfolio file
def get_portfolio_data():
    return {
        "cash_balance" : portfolio.cash_balance,
        "portfolio_value" : portfolio.portfolio_value(),
        "holdings" : portfolio.holdings,
        "transactions": portfolio.transactions,
        "limit_orders": portfolio.limit_orders
    }

# computes portfolio allocations, PL, and returns a summary of current holdings
def get_portfolio_summary():
    data = []
    
    # extract assets from portfolio
    total_value = portfolio.portfolio_value()
    cash_balance = portfolio.cash_balance

    total_pl = 0
    total_invested = 0

    # loop through each holding
    for ticker, (shares, avg_price) in portfolio.holdings.items():

        # calculate statistics
        cur_price = get_price(ticker)
        cur_val = round(cur_price * shares, 2)
        profit_loss = round((cur_price - avg_price) * shares, 2)
        profit_loss_percent = round ((profit_loss / (avg_price * shares)) * 100, 2) if avg_price > 0 else 0
        allocation_percent = round((cur_val / total_value) * 100, 2) if total_value > 0 else 0

        total_pl += profit_loss
        total_invested += avg_price * shares
        if total_invested > 0:
            total_pl_percent = round((total_pl / total_invested) * 100, 2)
        else:
            total_pl_percent = 0

        data.append({
        "ticker": ticker,
        "shares": shares,
        "current_value": cur_val,
        "profit_loss" : profit_loss,
        "profit_loss_percent" : profit_loss_percent,
        "allocation_percent" : allocation_percent
        })

    return {
        "total_value" : round(total_value, 2),
        "cash_balance" : round(cash_balance, 2),
        "allocations" : data,
        "total_profit_loss": round(total_pl, 2),
        "total_profit_loss_percent": total_pl_percent
    }

# buy stock given ticker and num shares
def buy_stock(ticker: str, shares: int):
    price = get_price(ticker)
    if price is None:
        return {"error": f"Ticker {ticker} not found."} # returns an http response body in JSON

    cost = price * shares
    if portfolio.cash_balance < cost:
        return {"error": f"Insufficient funds to buy {shares} of {ticker}."}
    
    # call functions from /cli_src
    portfolio.buy_stock(ticker, shares)
    portfolio.save_file(portfolio_file)
    return {"message": f"Bought {shares} shares of {ticker} at price ${price}", "price": price}

# sell stock
def sell_stock(ticker: str, shares: int):
    # get latest price
    price = get_price(ticker)
    if price is None:
        return {"error": f"Ticker {ticker} not found."}

    if ticker not in portfolio.holdings or portfolio.holdings[ticker][0] < shares: 
        return {"error": f"Insufficient shares to sell {shares} of {ticker}."}
    
    portfolio.sell_stock(ticker, int(shares))

    # ensure zero-share positions are removed from holdings
    pos = portfolio.holdings.get(ticker)
    if pos and int(pos[0]) <= 0:
        del portfolio.holdings[ticker]

    # persist
    portfolio.save_file(portfolio_file)
    return {"message": f"Sold {shares} shares of {ticker} at price ${price}", "price": price}

# use cli_src function to queue limit orders
def add_limit_order(ticker: str, shares: int, price: float, order_type: str):
    portfolio.queue_limit_order(ticker, shares, price, order_type) # call fnc
    portfolio.save_file(portfolio_file)
    # for message purposes
    if order_type == 'LB':
        order_type_text = 'Limit Buy'
    elif order_type == 'SB':
        order_type_text = 'Stop Buy'
    elif order_type == 'LS':
        order_type_text = 'Limit Sell'
    else:
        order_type_text = 'Stop Loss'
    return {"message": f"Queued {shares} shares of {ticker} for {order_type_text} at ${price}"}

# run query_limit_buy_sell on demand for each order 
def run_limit_checks():
    tickers = set(order["ticker"] for order in portfolio.limit_orders)
    for ticker in tickers:
        portfolio.query_limit_buy_sell(ticker)
    portfolio.save_file(portfolio_file)

# get price and return as json
def get_price_json(ticker: str):
    price = get_price(ticker)
    if price is None:
        return {"error": "Invalid symbol or price not available."}
    return {"symbol": ticker, "price": price}

def generate_stock_chart(symbol: str, period: str, outpath: str) -> str:
    # create folder if doesn't exist
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    
    # generate and save chart
    plot_stock_price(symbol, period, save_path=outpath) # from data.plotting
    return "/static/chart.html" # return the path of the generated chart

# deposit more buying power into account
def deposit_funds(amount: float):
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return {"error": "Invalid Amount"}
    
    if amount <= 0:
        return {"error" : "Amount must be positive."}
    
    # update cash balance
    portfolio.cash_balance += amount
    portfolio.transactions.append({
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "DEPOSIT",
        "ticker": "CASH",
        "shares": round(amount, 2),
        "price": round(amount, 2)
    })
    portfolio.save_file(portfolio_file)
    return {"message": f"Deposited ${round(amount, 2)} successfully to cash balance. Please give some time for cash to settle."}
   
# withdraw buying power from account, essentially removing money
def withdraw_funds(amount: float):
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return {"error": "Invalid Amount"} 
    if amount <= 0:
        return {"error" : "Amount must be positive."}
    # update cash balance
    portfolio.cash_balance -= amount
    portfolio.transactions.append({
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "WITHDRAW",
        "ticker": "CASH",
        "shares": round(amount, 2),
        "price": round(amount, 2)
    })
    portfolio.save_file(portfolio_file)
    return {"message": f"Withdrew ${round(amount, 2)} successfully. Please give some time for cash to settle."}

# create transactions.txt file from portfolio.transactions
def format_transactions_text() -> str:
    lines = []
    for tx in portfolio.transactions:
        t = tx.get("time", "")
        typ = tx.get("type", "")
        sh = tx.get("shares", 0)
        tk = tx.get("ticker", "")
        pr = tx.get("price", 0)
        lines.append(f"{t} - {typ} {sh} {tk} @ ${pr}")
    return "\n".join(lines)

# WATCHLIST LOGIC
def load_watchlist() -> list:
    if os.path.exists(watchlist_file):
        with open(watchlist_file, "r") as fp:
            return sorted({ticker.strip().upper() for ticker in fp if ticker.strip()}) # return sorted list of tickers in the watchlist. 
    return []

def save_watchlist(tickers: list):
    with open(watchlist_file, "w") as fp:
        fp.write("\n".join(sorted({ticker.upper() for ticker in tickers})))

def reload_watchlist():
    """Reload watchlist from disk into memory and return it."""
    global watchlist
    watchlist = load_watchlist()
    return watchlist

watchlist = load_watchlist()

def get_watchlist() -> dict[str, list[str]]:
    # always read from disk so uploads show up immediately
    return {"tickers": reload_watchlist()}

def add_to_watchlist(ticker: str) -> dict[str, object]:
    if not ticker or not isinstance(ticker, str):
        return {"error": "Invalid ticker.", "tickers": watchlist}
    new_t = ticker.strip().upper()
    if not new_t:
        return {"error": "Invalid ticker.", "tickers": watchlist}
    if new_t in watchlist:
        return {"message": f"{new_t} already in watchlist.", "tickers": watchlist}
    watchlist.append(new_t)
    save_watchlist(watchlist)
    return {"message": f"Added {new_t} to watchlist.", "tickers": watchlist}

def remove_from_watchlist(ticker: str):
    if not ticker or not isinstance(ticker, str):
        return {"error": "Invalid ticker.", "tickers": watchlist}
    new_t = ticker.strip().upper()
    if new_t in watchlist:
        watchlist.remove(new_t)
        save_watchlist(watchlist)
        return {"message": f"Removed {new_t} from watchlist.", "tickers": watchlist}
    return {"error": f"{new_t} not in watchlist.", "tickers": watchlist}
