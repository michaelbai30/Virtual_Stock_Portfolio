# Virtual Stock Portfolio Trader and Viewer

Developer: Michael Bai

This is a full-stack stock "paper" trading simulator that lets you buy, sell, and analyze real-time stock market data using the [Yahoo Finance API](https://pypi.org/project/yfinance/). 

It supports technical indicators, visualizations, portfolio tracking, limit/stop orders, and a persistent holdings storage system.

The goal of this app is to enable individuals to practice trading strategies on the market with fake "paper" money, as well as perform basic stock analysis.

Live Demo Hosted on Render: https://virtual-stock-portfolio-web-app.onrender.com/
(Note: On free tiers, the service sleeps when inactive, so allow for ~30–60 seconds for the server to cold-start)

---

## Tech Stack

### Backend
- **Python**
- **Flask** – REST API
- **yfinance** – Real-time stock data
- **Plotly** – For data visualization

### Frontend
- **HTML, CSS, JavaScript**

### Deployment
- **Render with Gunicorn**

---

## Current Features
- ✅ Buy/Sell stocks using real-time prices  
- ✅ Store and persist all transactions under portfolio.txt and watchlist.txt.
- ✅ View current portfolio and cash balance (buying power)
- ✅ Limit/Stop Buy & Sell orders (auto-executed)
- ✅ Portfolio profit/loss summary
- ✅ Visualize individual stock price charts with:
  - Candlesticks
  - Moving Averages (MA10, MA50, MA200)
  - RSI (Relative Strength Index)


---
## High Level App Structure
```
server/
  app.py                 # Flask app + routes
  logic.py               # Trading, portfolio, watchlist logic
  frontend/
    templates/index.html # HTML
    static/
      script.js          # Frontend logic & API calls
      style.css          # Styles
cli_src/
  ...                    # Original CLI portfolio logic & helpers
```

---

## Run Locally
1. Clone the repo  
2. Set up the Python virtual environment from the folder with requirements.txt:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run python3 app.py from the server folder.
4. Open the server hosted at http://127.0.0.1:5000

