# for command line version of the program
# no longer being worked on
from data.plotting import *
from portfolio.portfolio import Portfolio
from data.pricing import get_price
from utils.helpers import *
import warnings
import logging
warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

portfolio = Portfolio.load_file()
portfolio.display_portfolio()

for ticker in set(order["ticker"] for order in portfolio.limit_orders):
    portfolio.query_limit_buy_sell(ticker)

while True:
    action = input("Would you like to Purchase (P), Sell (S), Limit Order (L), View Stock (V), or No (N)? ").lower()

    if action == "p":
        handle_purchase(portfolio)
    elif action == "s":
        handle_sale(portfolio)
    elif action == "l":
        handle_limit_order(portfolio)
    elif action == "v":
        handle_plot_stock_price()
    elif action == "n":
        break
    else:
        print("Invalid option, please try again.")

portfolio.save_file() 