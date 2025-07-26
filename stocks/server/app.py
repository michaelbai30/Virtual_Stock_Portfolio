# init backend server
# define the URLs the app can respond to
# map URLs to functions in logic.py
# receive data from frontend and returns json

import os
import yfinance as yf
from flask import Flask, jsonify, request, render_template
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
    run_limit_checks
)
# initialize Flask web server
app = Flask(__name__, static_folder='frontend/static', static_url_path='/static', template_folder='frontend/templates')
CORS(app) 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/summary', methods=['GET'])
def summary():
    return jsonify(get_portfolio_summary())

@app.route('/api/portfolio', methods=['GET'])
def portfolio():
    run_limit_checks() # auto-trigger any queued orders before returning data
    # jsonify converts Python dict to JSON http
    return jsonify(get_portfolio_data()) 

@app.route('/api/price', methods=['GET'])
def price():
    symbol = request.args.get("symbol") 
    return jsonify(get_price_json(symbol))


@app.route('/api/buy', methods=['POST'])
def buy():
    data = request.json # ex request.json {"symbol" : "AAPL", "shares" : 5}
    return jsonify(buy_stock(data['symbol'], int(data['shares'])))

@app.route('/api/sell', methods=['POST'])
def sell():
    data = request.json
    return jsonify(sell_stock(data['symbol'], int(data['shares'])))

@app.route('/api/limit-order', methods=['POST'])
def limit_order():
    data = request.json
    return jsonify(add_limit_order(
        symbol=data['ticker'],
        shares=int(data['shares']),
        price=float(data['price']),
        order_type=data['order_type']
    ))

@app.route('/api/chart', methods=['GET'])
def chart():
    symbol = request.args.get('symbol')
    period = request.args.get('period', '1mo') # default to one month
    outpath = os.path.join(app.static_folder, "chart.html")
    try:
        path = generate_stock_chart(symbol, period, outpath)
        return jsonify({"image_path": path})
    except Exception as e:
        return jsonify({"error" : str(e)})

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

@app.route('/api/limit-order', methods=['POST'])
def place_limit_order():
    data = request.get_json()
    
    # extract from expectant json
    ticker = data.get('ticker')
    shares = int(data.get('shares', 0))
    price = float(data.get('price', 0))
    order_type = data.get('order_type')  # should be either LB, SB, LS, SL

    # condition checking
    if not ticker or shares <= 0 or price <= 0 or order_type not in ['LB', 'SB', 'LS', 'SL']:
        return jsonify({"error" : "Invalid Input"})

    res = add_limit_order(ticker, shares, price, order_type)

    return jsonify(res)
    
@app.route('/api/check-orders', methods=['GET'])
def check_orders():
    run_limit_checks()
    return jsonify({"message": "Queried for possible limit orders"})

if __name__ == '__main__':
    app.run(debug=True)