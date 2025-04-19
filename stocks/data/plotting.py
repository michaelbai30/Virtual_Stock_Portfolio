import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio

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
    
    try:
        info = stock.info
        if not info or info.get('regularMarketPrice') is None:
            raise ValueError
    except Exception:
        print(f"Invalid ticker '{ticker}'.")
        return


    stock_data = stock.history(period=yf_period, interval=interval)
    if stock_data.empty:
        print(f"No data found for {ticker} with period {period}")
        return
    
    fig = go.Figure(data=[go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'], high = stock_data['High'],
        close=stock_data['Close'], low = stock_data['Low'],
    )])

    fig.update_layout(
        title = f'{ticker} Price Over {period.upper()}',
        xaxis_title = 'Date',
        yaxis_title = 'Price ($)',
        template = 'plotly_dark',
        hovermode = 'x unified',
        width = 1200,
        height = 600
    )
    fig.show()

def interactive_stock_view(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")
    df.reset_index(inplace=True)

    fig = go.Figure()

    # Candlestick trace
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick',
        visible=True  
    ))

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Close'],
        mode='lines',
        name='Line',
        visible=False  
    ))
    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                x=0.1,
                y=1.15,
                buttons=[
                    dict(label="Candlestick",
                         method="update",
                         args=[{"visible": [True, False]},
                               {"title": f"{ticker} Candlestick Chart"}]),
                    dict(label="Line",
                         method="update",
                         args=[{"visible": [False, True]},
                               {"title": f"{ticker} Line Chart"}]),
                ],
                direction="down"
            )
        ],
        title=f"{ticker} Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark",
        height=600,
        width=1000
    )

    fig.show()
   