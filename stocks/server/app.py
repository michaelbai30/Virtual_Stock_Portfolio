"""
server/app.py — The Flask web server

Defines the JSON/file APIs used by the frontend.

Functions:
- GET  / -> index.html
- GET  /api/summary -> portfolio P/L and allocations
- GET  /api/portfolio -> gets cash, value, holdings, transactions, limit_orders
- GET  /api/price?symbol=... -> price JSON (helper)
- GET  /api/price/<ticker> -> price + day % change (yfinance.info)
- GET  /api/chart -> generate candlestick HTML
- POST /api/buy, /api/sell -> handles market orders
- POST /api/limit-order -> queue LB/SB/LS/SL orders
- GET  /api/check-orders -> poll or execute pending limit/stop orders
- POST /api/deposit, /api/withdraw
- GET  /api/transactions.txt -> download human-readable log
- GET  /api/portfolio.txt -> download raw JSON portfolio
- GET  /api/watchlist.txt -> download raw watchlist
- POST /api/portfolio/upload -> validate + replace portfolio.txt, then reload
- POST /api/watchlist/upload -> validate + replace watchlist.txt
- GET/POST/DELETE /api/watchlist[...] -> watchlist CRUD operations

Notes:
- Uses logic.py for all portfolio/watchlist operations and file paths.
- After uploads, reload_portfolio() keeps state in sync with disk.
"""

import os
import json
import yfinance as yf
import re
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
from logic import( 
    get_portfolio_data,
    get_portfolio_summary,
    buy_stock,
    sell_stock,
    add_limit_order,
    run_limit_checks,
    get_price_json,
    generate_stock_chart,
    add_limit_order,
    run_limit_checks,
    deposit_funds,
    withdraw_funds,
    format_transactions_text,
    get_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
    reload_portfolio,
    portfolio_file,
    watchlist_file
)
# initialize Flask web server
app = Flask(__name__, static_folder='frontend/static', static_url_path='/static', template_folder='frontend/templates')
CORS(app) 

# app route decorators define API endpoints (URLS)
@app.route('/')
def home():
    return render_template('index.html')

# return JSON containing portfolio total value, cash balance, and allocations
@app.route('/api/summary', methods=['GET'])
def summary():
    reload_portfolio()
    # jsonify converts Python dict to JSON http
    return jsonify(get_portfolio_summary())

# get portfolio data as a json
@app.route('/api/portfolio', methods=['GET'])
def portfolio():
    reload_portfolio()
    run_limit_checks() # auto-trigger any queued orders before returning data
    return jsonify(get_portfolio_data()) 

# handles request to /api/price
@app.route('/api/price', methods=['GET'])
def price():
    ticker = request.args.get("symbol") # get the ticker from the url and passs to get_price_json
    return jsonify(get_price_json(ticker))

# handles requests to buy stock
@app.route('/api/buy', methods=['POST'])
def buy():
    data = request.json # ex request.json {"symbol" : "AAPL", "shares" : 5}
    return jsonify(buy_stock(data['symbol'], int(data['shares'])))

# handles requests to sell stock
@app.route('/api/sell', methods=['POST'])
def sell():
    data = request.json
    return jsonify(sell_stock(data['symbol'], int(data['shares'])))

# handles request to generate chart
@app.route('/api/chart', methods=['GET'])
def chart():
    ticker = request.args.get('symbol')
    period = request.args.get('period', '1mo') # default to one month
    outpath = os.path.join(app.static_folder, "chart.html")
    try:
        path = generate_stock_chart(ticker, period, outpath)
        return jsonify({"image_path": path})
    except Exception as e:
        return jsonify({"error" : str(e)})

# handles request to get price and percent change
@app.route('/api/price/<ticker>', methods=['GET'])
def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.info
        return jsonify({
            "ticker": ticker.upper(),
            "price": round(data["regularMarketPrice"], 2),
            "change_percent": round(data["regularMarketChangePercent"], 2)
        })
    except:
        return jsonify({"error" : "Invalid ticker"})

# handles limit order requests
@app.route('/api/limit-order', methods=['POST'])
def place_limit_order():
    data = request.get_json()
    
    # extract from expectant json
    ticker = data.get('ticker')
    shares = int(data.get('shares', 0))
    price = float(data.get('price', 0))
    order_type = data.get('order_type')  # should be either LB, SB, LS, SL

    # validate inputs
    if not ticker or shares <= 0 or price <= 0 or order_type not in ['LB', 'SB', 'LS', 'SL']:
        return jsonify({"error" : "Invalid Input"})

    res = add_limit_order(ticker, shares, price, order_type)

    return jsonify(res)

# check for possible limit orders
@app.route('/api/check-orders', methods=['GET'])
def check_orders():
    run_limit_checks()
    return jsonify({"message": "Queried for possible limit orders"})

# deposit funds
@app.route('/api/deposit', methods=['POST'])
def api_deposit():
    data = request.get_json()
    amount = data.get('amount', 0)
    return jsonify(deposit_funds(amount))

# withdraw funds
@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    data = request.get_json()
    amount = data.get('amount', 0)
    return jsonify(withdraw_funds(amount))

# endpoint to download transactions.txt
@app.route('/api/transactions.txt', methods=['GET'])
def download_transactions_txt():
    text = format_transactions_text()
    return Response(
        text,
        headers={'Content-Disposition': 'attachment; filename=transactions.txt'} # download as a txt file attachment
    )

# WATCHLIST APIS
@app.route('/api/watchlist', methods=['GET'])
def api_get_watchlist():
    return jsonify(get_watchlist())

@app.route('/api/watchlist', methods=['POST'])
def api_add_to_watchlist():
    data = request.get_json()
    symbol = data.get('symbol')
    return jsonify(add_to_watchlist(symbol))

@app.route('/api/watchlist/<symbol>', methods=['DELETE'])
def api_remove_from_watchlist(symbol):
    return jsonify(remove_from_watchlist(symbol))


# DOWNLOAD RAW FILES
@app.route('/api/portfolio.txt', methods=['GET'])
def download_portfolio_txt():
    try:
        with open(portfolio_file, "r") as fp:
            content = fp.read() # return raw
    except FileNotFoundError:
        content = '{"holdings": {}, "cash_balance": 0, "transactions": [], "limit_orders": []}'

    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=portfolio.txt"}
    )

@app.route('/api/watchlist.txt', methods=['GET'])
def download_watchlist_txt():
    try:
        with open(watchlist_file, "r") as fp:
            content = fp.read()
    except FileNotFoundError:
        content = "[]"
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=watchlist.txt"}
    )

# UPLOAD AND VALIDATE FILES
TICKER_RE = re.compile(r'^[A-Z][A-Z0-9.\-]{0,9}$') # < 10 chars max, letters, digits, ., -, must start with a letter.
def _is_number(n): return isinstance(n, (int, float)) and not isinstance(n, bool)

@app.route('/api/portfolio/upload', methods=['POST'])
def upload_portfolio_txt():
    # basic file checks
    if "file" not in request.files:
        return jsonify(ok=False, error="No file in request."), 400
    fp = request.files["file"]
    if not fp or fp.filename == "":
        return jsonify(ok=False, error="No file selected."), 400

    # filename is exactly 'portfolio.txt'
    fname = secure_filename(fp.filename)
    if fname != "portfolio.txt":
        return jsonify(ok=False, error="File must be named 'portfolio.txt'."), 400

    # check file is in UTF-8 format
    try:
        text = fp.read().decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return jsonify(ok=False, error="File must be UTF-8 text."), 400

    # must be JSON object
    try:
        obj = json.loads(text)
    except Exception:
        return jsonify(ok=False, error="Portfolio must be valid JSON."), 400
    if not isinstance(obj, dict):
        return jsonify(ok=False, error="Portfolio JSON must be a dict object."), 400

    # validate required keys
    # require 'holdings'
    if "holdings" not in obj or not isinstance(obj["holdings"], dict):
        return jsonify(ok=False, error="Portfolio must include a 'holdings' object."), 400
    # require 'cash_balance'
    if "cash_balance" not in obj or not _is_number(obj["cash_balance"]):
        return jsonify(ok=False, error="Portfolio must include numeric 'cash_balance'."), 400
    # transactions & limit_orders can be empty lists but must exist
    if "transactions" not in obj or not isinstance(obj["transactions"], list):
        return jsonify(ok=False, error="Portfolio must include 'transactions' (array)."), 400
    if "limit_orders" not in obj or not isinstance(obj["limit_orders"], list):
        return jsonify(ok=False, error="Portfolio must include 'limit_orders' (array)."), 400

    # validate holdings
    # example: {"AAPL": [shares, avg_price], ...}
    invalid_holdings = []
    for t, val in obj["holdings"].items():
        if not isinstance(t, str) or not TICKER_RE.match(t.upper()):
            invalid_holdings.append(f"{t} (invalid ticker format)")
            continue
        # item must be a list/tuple
        # with exactly 2 items
        # item 0 = shares, which must be an int greater than or equal to 0
        # item 1 = avg_price, which must a num greater than or equal to 0
        if not (isinstance(val, (list, tuple)) and len(val) == 2 and
                isinstance(val[0], int) and _is_number(val[1]) and val[0] >= 0 and val[1] >= 0):
            invalid_holdings.append(f"{t} (expected [shares:int>=0, avg_price:number>=0])")
    if invalid_holdings:
        return jsonify(ok=False, error="Invalid holdings: " + ", ".join(invalid_holdings[:5])), 400

    # validate transactions
    invalid_tx = 0
    for tx in obj["transactions"]:
        if not isinstance(tx, dict):
            invalid_tx += 1; 
            break
        if not isinstance(tx.get("type"), str): 
            invalid_tx += 1; 
            break
        t = tx.get("ticker")
        if not isinstance(t, str) or not (t.upper() == "CASH" or TICKER_RE.match(t.upper())):
            invalid_tx += 1; 
            break
        if not _is_number(tx.get("shares", 0)) or not _is_number(tx.get("price", 0)):
            invalid_tx += 1; 
            break
        if not isinstance(tx.get("time", ""), str):
            invalid_tx += 1; 
            break

    if invalid_tx:
        return jsonify(ok=False, error="Invalid 'transactions' entries."), 400

    # validate limit_orders (allow empty)
    invalid_lo = 0
    for lo in obj["limit_orders"]:
        if not isinstance(lo, dict):
            invalid_lo += 1; 
            break
        if not isinstance(lo.get("type"), str): 
            invalid_lo += 1; 
            break
        t = lo.get("ticker")
        if not isinstance(t, str) or not TICKER_RE.match(t.upper()):
            invalid_lo += 1; 
            break
        if not _is_number(lo.get("shares", 0)) or not _is_number(lo.get("price", 0)):
            invalid_lo += 1; 
            break
        if not isinstance(lo.get("time", ""), str):
            invalid_lo += 1; 
            break
    if invalid_lo:
        return jsonify(ok=False, error="Invalid 'limit_orders' entries."), 400

    # write raw content
    with open(portfolio_file, "wb") as out:
        out.write(text.encode("utf-8"))

    # reload portfolio
    try:
        reload_portfolio()
    except Exception:
        pass
    return jsonify(ok=True), 200


MAX_WATCHLIST = 500 # for safety reasons
@app.route('/api/watchlist/upload', methods=['POST'])
def upload_watchlist_txt():
    # basic file checks
    if "file" not in request.files:
        return {"error": "No file in requests"}, 400
    fp = request.files["file"]
    if not fp or fp.filename == "":
        return {"error": "No file selected."}, 400

    # file name is exactly 'watchlist.txt'
    fname = secure_filename(fp.filename)
    if fname != "watchlist.txt":
        return {"error": "File must be named 'watchlist.txt'."}, 400

    # check file is in UTF-8 format
    try:
        text = fp.read().decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return {"error": "File must be UTF-8 text."}, 400

    # reject potential JSON file formatting.
    if "{" in text or "}" in text:
        return {"error": "This looks like a portfolio JSON file. Upload a plain-text watchlist (tickers separated by new lines, or any whitespace)."}, 400

    # split on ANY whitespace including new lines and normalize to uppercase
    tokens = re.split(r"\s+", text.strip())
    tokens = [t.upper() for t in tokens if t.strip()]

    if not tokens:
        return {"error": "Empty Watchlist."}, 400
    if len(tokens) > MAX_WATCHLIST:
        return {"error": f"Too many tickers (> {MAX_WATCHLIST}). Aborting for safety reasons."}, 400

    # validate and remove duplicates if needed
    symbols = []
    seen = set()
    invalid = []
    for t in tokens:
        if t in seen:
            continue
        if not TICKER_RE.match(t):
            invalid.append(t)
            continue
        seen.add(t)
        symbols.append(t)

    if invalid:
        sample = ", ".join(invalid[:5])
        return {"error": f"Invalid ticker(s): {sample}. Valid tickers are to be composed of A–Z, 0–9, '.', '-' (max 10 chars)"}, 400

    # save in one per line format
    content = "\n".join(symbols) + "\n"
    with open(watchlist_file, "w") as out:
        out.write(content)

    return {"ok": True, "count": len(symbols)}

if __name__ == '__main__':
    app.run(debug=True)
