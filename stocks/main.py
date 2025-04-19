#TODO handle errors when ticker not present
from analysis.indicators import calculate_quant_score
from data.plotting import *
from portfolio.portfolio import Portfolio
from data.pricing import get_price
from utils.helpers import *
import warnings
import logging
warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

tickers = ["QQQ", "MRVL", "CRWD", "SPOT", "META", "IBM", "ACHR", "COST", "NKE", "SPY", "AAPL", "TSLA", "NVDA", "AMD", "AMZN", "NFLX", "CRWD", "STEM", "SOFI", "TSM", "MSFT", "GME"]

portfolio = Portfolio.load_file()
portfolio.display_portfolio()
portfolio.display_portfolio_graph()
portfolio.display_allocations()
plot_stock_price("AAasdPL", "5y")
interactive_stock_view("AAPL")
for ticker in tickers:
    print(f'{ticker}: {calculate_quant_score(ticker)}\n')

for ticker in set(order["ticker"] for order in portfolio.limit_orders):
    portfolio.query_limit_buy_sell(ticker)

while True:
    action = input("Would you like to Purchase (P), Sell (S), Limit Order (L), or No (N)? ").lower()

    if action == "p":
        handle_purchase(portfolio)
    elif action == "s":
        handle_sale(portfolio)
    elif action == "l":
        handle_limit_order(portfolio)
    elif action == "n":
        break
    else:
        print("Invalid option, please try again.")

portfolio.save_file()  # Save file when the user decides to exit
