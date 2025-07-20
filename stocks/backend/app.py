# init backend server
# define the URLs the app can respond to
# map URLs to functions in logic.py
# receive data from frontend and returns json

from flask import Flask, jsonify, request
from flask_cors import CORS
from logic import( 
    get_portfolio_data,
    buy_stock,
    sell_stock,
    add_limit_order,
    run_limit_checks,
    get_price_json
)

# initialize Flask web server
app = Flask(__name__)
CORS(app) # enables web apps to request resources from different domains than that of the host webpage

@app.route('/')
def home():
    return 'Testing: This is home'

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
        symbol=data['symbol'],
        shares=int(data['shares']),
        price=float(data['price']),
        order_type=data['order_type']
    ))

if __name__ == '__main__':
    app.run(debug=True)