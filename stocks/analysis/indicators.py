import statistics
import numpy as np
import yfinance as yf
#TODO error proof these 

def calculate_RSI(ticker, period=14):

    try:
        if period <= 0:
            raise ValueError("Period must be a valid integer.")
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period=f"{period + 1}d")  # need period + 1 to get period changes
        if stock_data.empty or 'Close' not in stock_data:
            print(f"No data found for ticker {ticker}")
            return None
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
    except ValueError as e:
        print(f"{e}")
        return None
    except Exception as e:
        print(f"Error {e}")
        return None

def calculate_sharpe(ticker):
    try:

        stock = yf.Ticker(ticker)
        stock_data = stock.history(period='3y')
        if stock_data.empty or 'Close' not in stock_data:
            print(f"No data found for ticker {ticker}")
            return None
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
        if std_dev == 0:
            print("Divide by zero error.")
            return None
        annualized_return = avg_daily_returns * 252
        annualized_volatility = std_dev * np.sqrt(252)
        sharpe = (annualized_return - rfr) / annualized_volatility
        return sharpe
    except Exception as e:
        print(f"Error: {e}")
        return None

def calculate_sortino(ticker):
    try:
        
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period='3y')
        if stock_data.empty or 'Close' not in stock_data:
            print(f"No data found for ticker {ticker}")
            return None
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
        if std_dev == 0:
            print("Divide by zero error.")
            return None
        annualized_return = avg_daily_returns * 252
        annualized_volatility = std_dev * np.sqrt(252)
        if annualized_volatility == 0:
            return float('inf')
        sortino = (annualized_return - rfr) / annualized_volatility
        return sortino
    except Exception as e:
        print(f"Error: {e}")
        return None


def calculate_maximum_drawdown(ticker):
    try:
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period='5y')

        if stock_data.empty or 'Close' not in stock_data.columns:
            print(f"No data found for ticker {ticker}")
            return None

        max_drawdown = 0
        running_max = stock_data['Close'].iloc[0]

        for i in range(1, len(stock_data)):
            current_price = stock_data['Close'].iloc[i]
            running_max = max(running_max, current_price)
            if running_max != 0:
                drawdown = (running_max - current_price) / running_max
                max_drawdown = max(max_drawdown, drawdown)

        return round(max_drawdown * 100, 2)

    except Exception as e:
        print(f"Error: {e}")
        return None



def calculate_calmar_ratio(ticker):
    try:
        
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period='3y')
        if stock_data.empty or 'Close' not in stock_data.columns:
            print(f"No data found for ticker {ticker}")
            return None
        
        max_drawdown = 0
        running_max = stock_data['Close'].iloc[0]

        if len(stock_data) < 2:
            return None
        daily_returns = []
        for i in range(1, len(stock_data)):
            daily_return = ((stock_data['Close'].iloc[i] - stock_data['Close'].iloc[i - 1]) / stock_data['Close'].iloc[i - 1]) * 100
            daily_returns.append(daily_return)

            running_max = max(running_max, stock_data['Close'].iloc[i])
            if running_max != 0:
                drawdown = (running_max - stock_data['Close'].iloc[i]) / running_max
                max_drawdown = max(max_drawdown, drawdown)
        annualized_return = np.mean(daily_returns) * 252
        if max_drawdown == 0:
            return float('inf')
        return annualized_return / abs(max_drawdown)
    except Exception as e:
        print(f"Error: {e}")
        return None

def calculate_quant_score(ticker):
    if not ticker:
        return
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