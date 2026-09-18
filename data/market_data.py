
#Imports live data from the Yahoo Finance API
import yfinance as yf
import pandas as pd
from utils.logger import logger



def get_current_price(ticker):

    #Basic checks to ensure inputs are valid
    if not isinstance(ticker, str):
        raise TypeError("Ticker symbol must be a string.")

    ticker = ticker.upper().strip()

    if not ticker:
        raise ValueError("Ticker symbol cannot be empty.")

    logger.info("Fetching current price for %s", ticker)

    #Finds the stock name using built in systems
    stock = yf.Ticker(ticker)

    #Finds the one day history (Open, Close, High, Low, Volume) of the stock
    history = stock.history(period="1d")

    if history.empty:
        logger.warning("No current market data found for %s", ticker)

        raise ValueError(f"No data found for ticker: {ticker}")

    #Returns the latest closing price of the stock
    current_price = history['Close'].iloc[-1]

    return float(current_price)

#Returns historical prices for a given ticker over a year
def get_historical_prices(ticker, period="1y"):
    if not isinstance(ticker, str):
        raise TypeError("Ticker symbol must be a string.")

    ticker = ticker.upper().strip()

    if not ticker:
        raise ValueError("Ticker symbol cannot be empty.")

    logger.info("Fetching %s historical data for %s", period, ticker)

    stock = yf.Ticker(ticker)

    #Takes in the stock's year long history
    history = stock.history(period=period)

    if history.empty:
        logger.warning("No historical data found for %s", ticker)

        raise ValueError(f"No historical market data found for ticker: {ticker}")

    return history

#Returns just the Close column of a stock's historical prices; all we really need
def get_closing_prices(ticker, period="1y"):
    history = get_historical_prices(ticker, period)

    return history["Close"]

#Returns historical prices given a specfic date, not just a time frame
def get_historical_prices_by_date(ticker, start, end):
    if not isinstance(ticker, str):
        raise TypeError("Ticker symbol must be a string.")

    ticker = ticker.upper().strip()

    if not ticker:
        raise ValueError("Ticker symbol cannot be empty.")

    stock = yf.Ticker(ticker)

    history = stock.history(start=start, end=end)

    if history.empty:
        raise ValueError(f"No historical market data found for ticker: {ticker}")

    return history

#Gets mutliple closing prices from a tuple of tickers
def get_multiple_closing_prices(tickers, period="1y"):
    logger.info("Fetching historical prices for %d tickers",len(tickers))

    if not isinstance(tickers, (list, tuple)):
        raise TypeError("Tickers must be provided as a list or tuple.")

    if not tickers:
        raise ValueError("Ticker list cannot be empty.")

    prices = {}

    for ticker in tickers:
        prices[ticker] = get_closing_prices(ticker,period)

    result = pd.DataFrame(prices).dropna()

    logger.info("Combined price dataset contains %d rows", len(result))

    return pd.DataFrame(prices).dropna()