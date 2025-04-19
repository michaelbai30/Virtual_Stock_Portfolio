import pandas as pd
import json
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import numpy as np
from data.pricing import get_price
import plotly.graph_objects as go

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

    def queue_limit_order(self, ticker, shares, target_price, order_type):
        order_type = order_type.upper()
        now = str(datetime.datetime.now())
        cost = target_price * shares

        order_map = {
            "LB": "LIMIT_BUY",
            "SB": "STOP_BUY",
            "LS": "LIMIT_SELL",
            "SL": "STOP_LOSS"
        }

        full_type = order_map.get(order_type)

        if not full_type:
            print("Did not queue limit order due to unsupported operation")
            return

        is_buy = full_type in ["LIMIT_BUY", "STOP_BUY"]
        is_sell = full_type in ["LIMIT_SELL", "STOP_LOSS"]

        if is_buy:
            if self.cash_balance >= cost:
                self.limit_orders.append({
                    "type": full_type,
                    "ticker": ticker,
                    "shares": shares,
                    "price": target_price,
                    "time": now
                })
                print(f"Queued {shares} shares of {ticker} to be bought at {target_price}")
            else:
                print("Insufficient funds!")

        elif is_sell:
            if ticker in self.holdings and self.holdings[ticker][0] >= shares:
                self.limit_orders.append({
                    "type": full_type,
                    "ticker": ticker,
                    "shares": shares,
                    "price": target_price,
                    "time": now
                })
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
                percent_loss = ((profit_loss / bought_val) * 100) if bought_val else 0.0
                pl_arr.append([ticker, profit_loss, percent_loss])

            return pl_arr
        else: 
            print("You currently have no holdings.")
            return
    
    def track_total_pl(self):
        total_cur = 0
        total_bought = 0
        if self.holdings:
            for ticker, val in self.holdings.items():
                total_cur += val[0] * get_price(ticker)
                total_bought += val[0] * val[1]
            profit_loss = total_cur - total_bought
            percent_loss = (((total_cur - total_bought) / (total_bought)) * 100) if total_bought else 0.0

            return [profit_loss, percent_loss]
        else: 
            print("You currently have no holdings.")
            return
             
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
            for tkr, pl_amt, pct_amt in self.track_pl_per_ticker():
                print(f"{tkr} PL: ${round(pl_amt, 2)} : {round(pct_amt, 2)}%")
        else:
            print("You currently have no holdings.")
            return

    def display_portfolio_graph(self):
        tickers = []
        pl_values = []
        pl_percents = []

        if self.holdings:
            for tkr, pl_amt, pct_amt in self.track_pl_per_ticker():
                tickers.append(tkr)
                pl_values.append(pl_amt)
                pl_percents.append(pct_amt)

        if not tickers:
            print("No data to display.")
            return
        fig = go.Figure(data=go.Bar(
            x= tickers,
            y = pl_values,
             hovertext = [f"Profit/Loss: ${round(val, 2)}<br>% Profit/Loss: {round(pct, 2)}%" for val, pct in zip(pl_values, pl_percents)],
            marker_color=['green' if val>=0 else 'red' for val in pl_values]
        ))

        fig.update_layout(
        title = 'Total Profit / Loss',
        xaxis_title = 'Stock',
        yaxis_title = 'Profit / Loss ($)',
        template = 'plotly_dark',
        hovermode = 'x unified',
        yaxis=dict(
            range=[min(pl_values) - 10, max(pl_values) + 10]  
        ),
        width = 1200,
        height = 600
    )
        fig.show()
        


    def display_allocations(self):
        labels = []
        values = []
        hover_texts = []

        for ticker, (shares, avg_price) in self.holdings.items():
            cur_price = get_price(ticker)
            total_value = shares * cur_price
            labels.append(ticker)
            values.append(total_value)
            hover_texts.append(
                f"Shares: {shares}<br>"
                f"Price: ${cur_price:.2f}<br>"
                f"Avg Price: ${avg_price:.2f}<br>"
                f"Value: ${total_value:,.2f}<br>"
                f"Percent Change: {(100 * ((cur_price - avg_price) / avg_price)):.2f}%"
            )
        if not values:
            print("No holdings to display.")
            return
        fig = go.Figure(
            data = [
                go.Pie(
                    labels = labels,
                    values = values,
                    hoverinfo = 'label+percent+text',
                    textinfo = 'label+percent',
                    textfont_size = 14,
                    hovertext = hover_texts
                )
            ]
        )

        fig.update_layout(
            title = "Portfolio Allocation",
            template = 'plotly_dark'

        )
        
        fig.show()

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