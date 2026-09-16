

import pandas as pd
import pytest
import numpy as np

from analytics.performance import calculate_annualized_volatility, calculate_cumulative_return, calculate_daily_returns, calculate_max_drawdown, calculate_max_drawdown, calculate_portfolio_returns, calculate_sharpe_ratio, calculate_sharpe_ratio


def test_calculate_daily_returns():
    prices = pd.Series([100, 110, 121])

    returns = calculate_daily_returns(prices)

    assert returns.iloc[0] == pytest.approx(0.10)
    assert returns.iloc[1] == pytest.approx(0.10)

def test_calculate_cumulative_return():
    prices = pd.Series([100, 110, 125])

    result = calculate_cumulative_return(prices)

    assert result == pytest.approx(0.25)

def test_annualized_volatility():
    returns = pd.Series([0.01, -0.01, 0.02, -0.02])

    result = calculate_annualized_volatility(returns)

    expected = returns.std() * np.sqrt(252)

    assert result == pytest.approx(expected)

def test_calculate_sharpe_ratio():
    returns = pd.Series([0.01, -0.005, 0.015, 0.002])

    volatility = returns.std() * np.sqrt(252)
    annualized_return = returns.mean() * 252

    expected = annualized_return / volatility

    result = calculate_sharpe_ratio(returns)

    assert result == pytest.approx(expected)

def test_max_drawdown():
    prices = pd.Series([100, 120, 90])

    result = calculate_max_drawdown(prices)

    assert result == pytest.approx(-0.25)

def test_calculate_portfolio_returns():
    returns = pd.DataFrame({
        "AAPL": [0.10, 0.00],
        "MSFT": [0.00, 0.10]
    })

    weights = {
        "AAPL": 0.60,
        "MSFT": 0.40
    }

    result = calculate_portfolio_returns(
        returns,
        weights
    )

    assert result.iloc[0] == pytest.approx(0.06)
    assert result.iloc[1] == pytest.approx(0.04)