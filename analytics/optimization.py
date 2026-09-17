

import numpy as np
import pandas as pd
from scipy.optimize import minimize


TRADING_DAYS = 252


def calculate_expected_returns(returns):
    return returns.mean() * TRADING_DAYS

def calculate_covariance_matrix(returns):
    return returns.cov() * TRADING_DAYS

def calculate_expected_portfolio_return(weights,expected_returns):
    return np.dot(weights,expected_returns)

def calculate_portfolio_volatility(weights,covariance_matrix):
    variance = np.dot(weights.T,np.dot(covariance_matrix,weights))

    return np.sqrt(variance)

def find_minimum_volatility_portfolio(
    expected_returns,
    covariance_matrix
):
    num_assets = len(expected_returns)

    initial_weights = np.array(
        [1 / num_assets] * num_assets
    )

    bounds = tuple(
        (0, 1)
        for _ in range(num_assets)
    )

    constraints = {
        "type": "eq",
        "fun": lambda weights:
            np.sum(weights) - 1
    }

    result = minimize(
        calculate_portfolio_volatility,
        initial_weights,
        args=(covariance_matrix,),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not result.success:
        raise ValueError(
            "Portfolio optimization failed."
        )

    return result.x

def negative_sharpe_ratio(
    weights,
    expected_returns,
    covariance_matrix,
    risk_free_rate=0.0
):
    portfolio_return = (
        calculate_expected_portfolio_return(
            weights,
            expected_returns
        )
    )

    portfolio_volatility = (
        calculate_portfolio_volatility(
            weights,
            covariance_matrix
        )
    )

    if portfolio_volatility == 0:
        return np.inf

    sharpe = (
        portfolio_return
        - risk_free_rate
    ) / portfolio_volatility

    return -sharpe

def find_maximum_sharpe_portfolio(
    expected_returns,
    covariance_matrix,
    risk_free_rate=0.0
):
    num_assets = len(expected_returns)

    initial_weights = np.array(
        [1 / num_assets] * num_assets
    )

    bounds = tuple(
        (0, 1)
        for _ in range(num_assets)
    )

    constraints = {
        "type": "eq",
        "fun": lambda weights:
            np.sum(weights) - 1
    }

    result = minimize(
        negative_sharpe_ratio,
        initial_weights,
        args=(
            expected_returns,
            covariance_matrix,
            risk_free_rate
        ),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not result.success:
        raise ValueError(
            "Portfolio optimization failed."
        )

    return result.x

def optimize_portfolio(
    returns,
    risk_free_rate=0.0
):
    expected_returns = (
        calculate_expected_returns(
            returns
        )
    )

    covariance_matrix = (
        calculate_covariance_matrix(
            returns
        )
    )

    min_vol_weights = (
        find_minimum_volatility_portfolio(
            expected_returns,
            covariance_matrix
        )
    )

    max_sharpe_weights = (
        find_maximum_sharpe_portfolio(
            expected_returns,
            covariance_matrix,
            risk_free_rate
        )
    )

    tickers = list(
        returns.columns
    )

    return {
        "minimum_volatility": {
            ticker: weight
            for ticker, weight
            in zip(
                tickers,
                min_vol_weights
            )
        },

        "maximum_sharpe": {
            ticker: weight
            for ticker, weight
            in zip(
                tickers,
                max_sharpe_weights
            )
        }
    }


