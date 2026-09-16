
#Imports live data from the Yahoo Finance API
import yfinance as yf

def get_current_price(ticker):

    #Basic checks to ensure inputs are valid
    if not isinstance(ticker, str):
        raise TypeError("Ticker symbol must be a string.")

    ticker = ticker.upper().strip()

    if not ticker:
        raise ValueError("Ticker symbol cannot be empty.")

    #Finds the stock name using built in systems
    stock = yf.Ticker(ticker)

    #Finds the one day history (Open, Close, High, Low, Volume) of the stock
    history = stock.history(period="1d")

    if history.empty:
        raise ValueError(f"No data found for ticker: {ticker}")

    #Returns the latest closing price of the stock
    current_price = history['Close'].iloc[-1]

    return float(current_price)

