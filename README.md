# Virtual Stock Portfolio Trader and Viewer

Author: Michael Bai

This is a full-stack stock "paper" trading simulator that lets you buy, sell, and analyze real-time stock market data using the [Yahoo Finance API](https://pypi.org/project/yfinance/). 

It supports technical indicators, visualizations, portfolio tracking, limit/stop orders, and a persistent holdings storage system (the CLI version of the app has these features).

The goal of this app is to enable individuals to practice trading strategies on the market with fake "paper" money, as well as perform stock analysis.

Eventually, I want to add budgeting app features (though I know the two concepts aren't really related 🤣). Maybe I'll make that into a different project.

---

## Evolution

This project began as a **pure Python command-line interface program**. I spent the last several months building out the logic, financial calculations / indicators, portfolio management tools, persistent portfolio saving and loading, and charting functionality.
These methods are found in the folder cli_src, which also includes a main.py that can be used to run the original CLI version of the application.

I am in the process of refactoring this cli code into a **full-stack web application**.
---

## Tech Stack

### Backend
- **Python**
- **Flask** – REST API
- **yfinance** – Real-time stock data
- **Plotly** – For data visualization
- **pandas / numpy** – For data analysis

### Frontend
- **HTML, CSS, JavaScript**
- (Maybe Soon?) **React.js** 

---

## Current Features (Both CLI and Web App)
- ✅ Buy/Sell stocks using real-time prices  
- ✅ Store and persist all transactions via JSON  
- ✅ View current portfolio and cash balance (buying power)
- ✅ Limit/Stop Buy & Sell orders (auto-executed)
- ✅ Portfolio profit/loss summary
- ✅ Visualize individual stock price charts with:
  - Candlesticks
  - Moving Averages (MA10, MA50, MA200)
  - RSI (Relative Strength Index)

## Current Features (CLI only as of now)
- ✅ Allocation pie charts and PL bar charts
---

## Installation
1. Clone the repo  
2. Set up the Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. Run python3 app.py from the server folder.
4. Open the server hosted at http://127.0.0.1:5000

For the original CLI version of the program...
Complete steps 1 and 2
Run main.py in cli_src
