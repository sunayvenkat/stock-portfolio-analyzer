

import pandas as pd
import numpy as np

#Calculates daily returns from a tuple of prices
def calculate_daily_returns(prices):
    return prices.pct_change().dropna()

#Calculates cumulative return from a tuple of prices
def calculate_cumulative_return(prices):
    if len(prices) < 2:
        raise ValueError("At least two price observations are required.")

    return (prices.iloc[-1] / prices.iloc[0]) - 1

def calculate_return_from_returns(returns):
    return (1 + returns).prod() - 1

#Calculates annual volatility off of returns
def calculate_annualized_volatility(returns):
    return returns.std() * np.sqrt(252)

#Calculates Sharpe ratio
def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    volatility = calculate_annualized_volatility(returns)

    if volatility == 0:
        raise ValueError("Volatility cannot be zero.")

    annualized_return = returns.mean() * 252

    return (annualized_return - risk_free_rate) / volatility

#Calculates how for a stock has fallen from its peak value
def calculate_drawdown(prices):
    running_max = prices.cummax()

    drawdown = (prices / running_max) - 1

    return drawdown

#Max drawdown of a price
def calculate_max_drawdown(prices):
    drawdown = calculate_drawdown(prices)

    return drawdown.min()

#Overall portfolio returns
def calculate_portfolio_returns(returns, weights):
    weight_series = pd.Series(weights)

    weight_series = weight_series.reindex(returns.columns)

    if weight_series.isna().any():
        raise ValueError("Weights must be provided for every ticker.")

    return returns.mul(weight_series, axis=1).sum(axis=1)

#Bundles everything for one stock into a dictionary
def analyze_performance(prices):
    returns = calculate_daily_returns(prices)

    return {
        "cumulative_return": calculate_cumulative_return(prices),
        "annualized_volatility": calculate_annualized_volatility(returns),
        "sharpe_ratio": calculate_sharpe_ratio(returns),
        "max_drawdown": calculate_max_drawdown(prices)
    }

def analyze_portfolio_returns(returns):
    growth = (1 + returns).cumprod()

    return {
        "cumulative_return":
            calculate_return_from_returns(returns),

        "annualized_volatility":
            calculate_annualized_volatility(returns),

        "sharpe_ratio":
            calculate_sharpe_ratio(returns),

        "max_drawdown":
            calculate_max_drawdown(growth)
    }

