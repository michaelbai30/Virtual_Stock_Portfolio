import pandas as pd
import json
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import statistics
import math
import numpy as np
class Portfolio:
    def __init__(self, initial_cash):
        self.cash_balance = initial_cash
        self.holdings = {}
        self.transactions = []
        self.limit_orders= []

    def buy_stock(self, ticker, shares):
        price_per_share = get_price(ticker)
        cost = shares * price_per_share
        if self.cash_balance >= cost:
            self.cash_balance -= cost
            if ticker in self.holdings:
                total_shares = self.holdings[ticker][0] + shares
                new_avg_price = (cost + self.holdings[ticker][0] * self.holdings[ticker][1]) / total_shares
                self.holdings[ticker] = [total_shares, round(new_avg_price, 2)]
                self.transactions.append({"type": "BUY", "ticker" : ticker, "shares" : shares, "price" : price_per_share, "time": str(datetime.datetime.now())})
            else:
                self.holdings[ticker] = [shares, price_per_share]
            print(f"Bought {shares} shares of {ticker} at ${price_per_share}")
        else:
            print("Insufficient funds!")

    def sell_stock(self, ticker, shares):
        if ticker in self.holdings and self.holdings[ticker][0] >= shares:
            price_per_share = get_price(ticker)
            self.holdings[ticker][0] -= shares
            self.cash_balance += shares * price_per_share
            print(f"Sold {shares} shares of {ticker} at ${get_price(ticker)}")
            self.transactions.append({"type": "SELL", "ticker" : ticker, "shares" : shares, "price" : price_per_share, "time": str(datetime.datetime.now())})
        else:
            print("Insufficient shares!")

    def queue_limit_buy(self, ticker, shares, target_price):
        cost = target_price * shares
        if self.cash_balance >= cost:
            self.limit_orders.append({"type": "LIMIT_BUY", "ticker" : ticker, "shares" : shares, "price" : target_price,  "time": str(datetime.datetime.now())})
            print(f"Queued {shares} shares of {ticker} to be bought at {target_price}")
        else:
            print("Insufficient funds!")

    def queue_limit_sell(self, ticker, shares, target_price):
        if ticker in self.holdings and self.holdings[ticker][0] >= shares:
            self.limit_orders.append({"type": "LIMIT_SELL", "ticker" : ticker, "shares" : shares, "price" : target_price,  "time": str(datetime.datetime.now())})
            print(f"Queued {shares} shares of {ticker} to be sold at {target_price}")
        else:
            print("Insufficient shares!")

    def queue_stop_buy(self, ticker, shares, target_price):
        cost = target_price * shares
        if self.cash_balance >= cost:
            self.limit_orders.append({"type": "STOP_BUY", "ticker" : ticker, "shares" : shares, "price" : target_price,  "time": str(datetime.datetime.now())})
            print(f"Queued {shares} shares of {ticker} to be bought at {target_price}")
        else:
            print("Insufficient funds!")

    def queue_stop_loss(self, ticker, shares, target_price):
        if ticker in self.holdings and self.holdings[ticker][0] >= shares:
            self.limit_orders.append({"type": "STOP_LOSS", "ticker" : ticker, "shares" : shares, "price" : target_price,  "time": str(datetime.datetime.now())})
            print(f"Queued {shares} shares of {ticker} to be sold at {target_price}")
        else:
            print("Insufficient shares!")

    def query_limit_buy_sell(self, ticker):
        cur_price = get_price(ticker)
        fulfilled_orders = []
        for order in self.limit_orders:
            if order["ticker"] != ticker:
                continue
            order["price"] = float(order["price"])
            order["shares"] = int(order["shares"])
            if order["type"] == "LIMIT_SELL" and cur_price >= order["price"]: # fulfill limit sell
                self.sell_stock(ticker, order["shares"])
                fulfilled_orders.append(order)
            elif order["type"] == "STOP_LOSS" and cur_price <= order["price"]:
                self.sell_stock(ticker, order["shares"])
                fulfilled_orders.append(order)
            elif order["type"] == "LIMIT_BUY" and cur_price <= order["price"]:
                self.buy_stock(ticker, order["shares"])
                fulfilled_orders.append(order)
            elif order["type"] == "STOP_BUY" and cur_price >= order["price"]:
                self.buy_stock(ticker, order["shares"])
                fulfilled_orders.append(order)
        for order in fulfilled_orders:
            self.limit_orders.remove(order)                                               


    def track_pl_per_ticker(self):
        pl_arr = []
        if self.holdings:
            for ticker, val in self.holdings.items():
                current_val = val[0] * get_price(ticker)
                bought_val = val[0] * val[1]

                profit_loss = current_val - bought_val
                percent_loss = ((current_val - bought_val) / (bought_val)) * 100
                pl_arr.append([ticker, profit_loss, percent_loss])

            return pl_arr
        else: 
            return
    
    def track_total_pl(self):
        total_cur = 0
        total_bought = 0
        if self.holdings:
            for ticker, val in self.holdings.items():
                total_cur += val[0] * get_price(ticker)
                total_bought += val[0] * val[1]
            profit_loss = total_cur - total_bought
            percent_loss = ((total_cur - total_bought) / (total_bought)) * 100

            return [profit_loss, percent_loss]
        else: 
            return
            
    def get_rt_updates(self, ticker, interval="5"):
        pass
    
    def high_price_alert(self, ticker, target_price):
        cur = get_price(ticker)
        if cur >= target_price:
            print(f"{ticker} has hit above your target price: ${cur}!")
    
    def low_price_alert(self, ticker, target_price):
        cur = get_price(ticker)
        if cur <= target_price:
            print(f"{ticker} has hit below your target price: ${cur}!")

    def portfolio_value(self):
        value = self.cash_balance
        if self.holdings:
            for ticker, val in self.holdings.items():
                value += val[0] * get_price(ticker)
        return value
        

    def display_portfolio(self):
        print("\nCurrent Portfolio:")
        print(f"Cash Balance: ${self.cash_balance:.2f}")
        print(f"Portfolio Value: ${round(self.portfolio_value(), 2)}")
        if self.holdings:
            for ticker, val in self.holdings.items():
                print(f"{ticker}: {str(val[0])} shares at average price {str(val[1])}, Total Value: ${round(val[0] * val[1],2)}")
                profit_loss_amt, percent_amt = self.track_total_pl()
            print(f"Total Profit/Loss: ${round(profit_loss_amt, 2)} : {round(percent_amt, 2)}%")
            arr = self.track_pl_per_ticker()
            for tkr, pl_amt, pct_amt in arr:
                print(f"{tkr} PL: ${round(pl_amt, 2)} : {round(pct_amt, 2)}%")

    def display_allocations(self):
        labels = []
        sizes = []
        for ticker, (shares, avg_price) in self.holdings.items():
            labels.append(ticker)
            sizes.append(shares * get_price(ticker))
        if not sizes:
            print("No holdings to display.")
            return
        plt.figure(figsize=(8,8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("Portfolio Allocation")
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig('allocations.png')
        plt.close()

    def save_file(self, filename="portfolio.txt"):
        with open(filename, 'w') as f:
            data = {
                'holdings' : self.holdings,
                'cash_balance' : self.cash_balance,
                'transactions' : self.transactions,
                'limit_orders' : self.limit_orders
            }
            json.dump(data, f)

    @classmethod 
    def load_file(cls, filename="portfolio.txt"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

                portfolio = cls(initial_cash = data['cash_balance'])
                portfolio.cash_balance = data['cash_balance']
                portfolio.holdings = data['holdings']
                portfolio.transactions = data['transactions']
                portfolio.limit_orders = data['limit_orders']
                return portfolio
        except FileNotFoundError:
            print(f"{filename} not found. Creating a new portfolio.")
            return cls(initial_cash=10000)
        

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    stock_data = stock.history(period='1d', interval="5m")
    # Convert the data to a pandas DataFrame
    stock_data = stock_data[['Close']]  # We’re interested in the "close" price

    stock_data.columns = ['Price']  # Renaming the column
    stock_data.index = pd.to_datetime(stock_data.index)  # Convert index to datetime format
    stock_data.index = stock_data.index.strftime('%y-%m-%d %H:%M:%S')
    stock_data = stock_data.rename_axis(f'{ticker} Time')
    stock_data['Price'] = pd.to_numeric(stock_data['Price']).round(2)
    stock_data = stock_data.tail(12)
    return stock_data

def get_price(ticker):
    stock = yf.Ticker(ticker)
    return round(stock.fast_info["lastPrice"], 2)
    
def display_tickers_price(tickers):
    for ticker in tickers:
        print(get_stock_data(ticker))

def calculate_RSI(ticker, period=14):
    stock = yf.Ticker(ticker)
    stock_data = stock.history(period=f"{period + 1}d")  # need period + 1 to get period changes
    closes = stock_data['Close'].tolist()

    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]

    gains = [change for change in changes if change > 0]
    losses = [abs(change) for change in changes if change < 0]

    if gains:
        avg_gain = statistics.mean(gains)
    else:
        avg_gain = 0
    if losses:
        avg_loss = statistics.mean(losses)
    else:
        avg_loss = 0

    if avg_loss == 0:
        return 100 # max RSI
    elif avg_gain == 0:
        return 0 # min RSI
    
    RS = avg_gain / avg_loss
    RSI = 100 - (100 / (1 + RS))
    return round(RSI, 2)

def calculate_sharpe(ticker):
    stock = yf.Ticker(ticker)
    stock_data = stock.history(period='3y')
    daily_returns = []
    for i in range(1, len(stock_data)):
        td_close = stock_data['Close'].iloc[i]
        yst_close = stock_data['Close'].iloc[i - 1]
        daily_return = ((td_close - yst_close) / yst_close) * 100
        daily_returns.append(daily_return)

    if len(daily_returns) == 0:
        return None
    
    avg_daily_returns = np.mean(daily_returns)
    rfr = 0.0001
    std_dev = np.std(daily_returns)
    annualized_return = avg_daily_returns * 252
    annualized_volatility = std_dev * np.sqrt(252)
    sharpe = (annualized_return - rfr) / annualized_volatility
    return sharpe

def calculate_sortino(ticker):
    stock = yf.Ticker(ticker)
    stock_data = stock.history(period='3y')
    daily_returns = []
    for i in range(1, len(stock_data)):
        td_close = stock_data['Close'].iloc[i]
        yst_close = stock_data['Close'].iloc[i - 1]
        daily_return = ((td_close - yst_close) / yst_close) * 100
        daily_returns.append(daily_return)

    if len(daily_returns) == 0:
        return None
    
    avg_daily_returns = np.mean(daily_returns)
    rfr = 0.0001
    negative_daily_returns = [element for element in daily_returns if element < 0]
    std_dev = np.std(negative_daily_returns)
    annualized_return = avg_daily_returns * 252
    annualized_volatility = std_dev * np.sqrt(252)
    if annualized_volatility == 0:
        return float('inf')
    sortino = (annualized_return - rfr) / annualized_volatility
    return sortino

def calculate_maximum_drawdown(ticker):
    stock = yf.Ticker(ticker)
    max_drawdown = 0
    running_max = 0 
    stock_data = stock.history(period='5y')
    for i in range(1, len(stock_data)):
        running_max = max(running_max, stock_data['Close'].iloc[i])
        drawdown = (running_max - stock_data['Close'].iloc[i]) / running_max
        max_drawdown = max(max_drawdown, drawdown)

    return round(max_drawdown * 100, 2)

def calculate_calmar_ratio(ticker):
    stock = yf.Ticker(ticker)
    max_drawdown = 0
    running_max = 0 
    stock_data = stock.history(period='3y')
    if len(stock_data) < 2:
        return None
    daily_returns = []
    for i in range(1, len(stock_data)):
        daily_return = ((stock_data['Close'].iloc[i] - stock_data['Close'].iloc[i - 1]) / stock_data['Close'].iloc[i - 1]) * 100
        daily_returns.append(daily_return)

        running_max = max(running_max, stock_data['Close'].iloc[i])
        drawdown = (running_max - stock_data['Close'].iloc[i]) / running_max
        max_drawdown = max(max_drawdown, drawdown)
    annualized_return = np.mean(daily_returns) * 252
    if max_drawdown == 0:
        return float('inf')
    return annualized_return / abs(max_drawdown)

def calculate_quant_score(ticker):
    try:
        rsi = calculate_RSI(ticker)
        sharpe = calculate_sharpe(ticker)
        sortino = calculate_sortino(ticker)
        max_drawdown = calculate_maximum_drawdown(ticker)
        calmar = calculate_calmar_ratio(ticker)
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return None

    # Normalize each metric to a 0–1 range
    rsi_score = max(0, 1 - abs(50 - rsi) / 50)  # Best if RSI ~ 30-40
    sharpe_score = min(sharpe / 2, 1)
    sortino_score = min(sortino / 2, 1)
    drawdown_score = max(0, 1 - max_drawdown)  # Lower drawdown = better
    calmar_score = min(calmar / 3, 1)

    # Weights
    score = (
        rsi_score * 15 +
        sharpe_score * 25 +
        sortino_score * 20 +
        drawdown_score * 15 +
        calmar_score * 25
    )

    return round(score, 2)

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
    stock_data = stock.history(period=yf_period, interval=interval)
    if stock_data.empty:
        print(f"No data found for {ticker} with period {period}")
        return
    
    plt.figure(figsize=(12,6))
    plt.plot(stock_data.index, stock_data['Close'], label=f"{ticker} Price")
    plt.title(f"{ticker} Stock Price Over {period.upper()}", fontsize=16)
    plt.xlabel("Date")
    plt.ylabel=("Price ($)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("Stock.png")

    plt.close()




tickers = ["SPY", "AAPL", "TSLA", "NVDA", "AMD", "AMZN", "NFLX", "CRWD", "STEM", "SOFI", "TSM", "MSFT", "GME"]

# display_tickers_price(tickers)
portfolio = Portfolio.load_file()
portfolio.display_portfolio()
portfolio.display_allocations()
plot_stock_price("AAPL", "5y")
for ticker in tickers:
    
    print(f'{ticker}: {calculate_quant_score(ticker)}\n')

for ticker in set(order["ticker"] for order in portfolio.limit_orders):
    portfolio.query_limit_buy_sell(ticker)

user_input = input("Would you like to purchase or sell a stock? P for Purchase, S for Sell, L for Limit Order, N for No ")
if user_input == "P" or user_input == "p":
    ticker_buy = input("Please enter the ticker of the stock you wish to purchase or enter N for No ")
    if (ticker_buy == "N" or ticker_buy == "n"):
        pass
    else:
        print(f"{ticker_buy} current price = {get_price(ticker_buy)} ")
        num_buy = input("Please enter the amount of stock you wish to purchase or enter N for No ")
        if (num_buy == "N" or num_buy == "n"):
            pass
        else:
            portfolio.buy_stock(ticker_buy, int(num_buy))
    
elif user_input == "S" or user_input == "s":
    ticker_sell = input("Please enter the ticker of the stock you wish to sell or enter N for No ")
    if (ticker_sell == "N" or ticker_sell == "n"):
        pass
    else:
        print(f"{ticker_sell} current price = {get_price(ticker_sell)} ")
        num_sell = input("Please enter the amount of stock you wish to sell or enter N for No ")
        if (num_sell == "N" or num_sell == "n"):
            pass
        else:
            portfolio.sell_stock(ticker_sell, int(num_sell))

elif user_input == "L" or user_input == "l":
    ticker_buy_sell = input ("Please enter the ticker of the stock or enter N for No ")
    if (ticker_buy_sell == "N" or ticker_buy_sell == "n"):
        pass
    else:
        print(f"{ticker_buy_sell} current price = {get_price(ticker_buy_sell)} ")
        order_type = input("Please enter the type of order: Limit Buy (LB), Limit Sell (LS), Stop Buy (SB), Stop Loss (SL) ")
        order_target_price = input("Please enter the target price ")
        order_target_price = float(order_target_price)
        num_shares = input("Please enter the amount of shares ")
        num_shares = int(num_shares)
        if order_type == "LB" or order_type == "lb": 
            portfolio.queue_limit_buy(ticker_buy_sell, num_shares, order_target_price)
        elif order_type == "LS" or order_type == "ls":
            portfolio.queue_limit_sell(ticker_buy_sell, num_shares, order_target_price)
        elif order_type == "SB" or order_type == "sb":
            portfolio.queue_stop_buy(ticker_buy_sell, num_shares, order_target_price)
        elif order_type == "SL" or order_type == "sl":
            portfolio.queue_stop_loss(ticker_buy_sell, num_shares, order_target_price)   
else:
    pass

portfolio.save_file(); 

