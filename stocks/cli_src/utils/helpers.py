"""
cli_src/utils/helpers.py

Small interactive wrappers around Portfolio for the command-line app.

Functions:
  - display_tickers_price(tickers): print recent price data via get_stock_data
  - display_current_holdings(ticker, portfolio): show live price & position
  - handle_purchase(portfolio): prompt to call portfolio.buy_stock(...)
  - handle_sale(portfolio): prompt to call portfolio.sell_stock(...)
  - handle_limit_order(portfolio): prompt to call queue LB/LS/SB/SL

Used by:
  - CLI entrypoints (e.g., cli_src/main.py) to drive the text UI.
  - Not used by the Flask web app.
"""
from portfolio.portfolio import Portfolio
from data.pricing import get_stock_data
from data.pricing import get_price

def display_tickers_price(tickers):
    for ticker in tickers:
        print(get_stock_data(ticker))

# for CLI app only
def display_current_holdings(ticker, portfolio):
    price = get_price(ticker)
    if price is None:
        print(f"'{ticker}' is not a valid ticker or price is unavailable.")
        return False

    print(f"{ticker.upper()} current price = ${price}")

    if ticker in portfolio.holdings:
        print(f"You currently have {portfolio.holdings[ticker][0]} shares of {ticker.upper()}.")
    else:
        print(f"You do not currently hold any shares of {ticker.upper()}.")

# for CLI app only
def handle_purchase(portfolio):
    ticker = input("Enter the ticker you wish to purchase (or N to cancel): ").upper()
    if ticker == "N":
        return
    success = display_current_holdings(ticker, portfolio)

    if success == False:
        return

    num = input("Enter number of shares to purchase (or N to cancel): ")
    if num.lower() == "n":
        return
    elif not num.isdigit():
        print("You did not enter an integer.")
        return
    portfolio.buy_stock(ticker, int(num))

# for CLI app only
def handle_sale(portfolio):
    ticker = input("Enter the ticker you wish to sell (or N to cancel): ").upper()
    if ticker == "N":
        return
    success = display_current_holdings(ticker, portfolio)
    if success == False:
        return
    if ticker not in portfolio.holdings or portfolio.holdings[ticker][0] == 0:
        return
    num = input("Enter number of shares to sell (or N to cancel): ")
    if num.lower() == "n":
        return
    elif not num.isdigit():
        print("You did not enter an integer.")
        return
    portfolio.sell_stock(ticker, int(num))

# for CLI app only
def handle_limit_order(portfolio):
    ticker = input("Enter the ticker for the limit/stop order (or N to cancel): ").upper()
    if ticker == "N":
        return
    success = display_current_holdings(ticker, portfolio)
    if success == False:
        return
    order_type = input("Enter order type: Limit Buy (LB), Limit Sell (LS), Stop Buy (SB), Stop Loss (SL) (or N to cancel): ").upper()
    if order_type.lower() == "n":
        return
    if order_type not in ["LB", "LS", "SB", "SL"]:
        print("Invalid order type.")
        return

    try:
        price = float(input("Enter target price: "))
        shares = int(input("Enter number of shares: "))
    except ValueError:
        print("Invalid number or price input.")
        return

    portfolio.queue_limit_order(ticker, shares, price, order_type)
