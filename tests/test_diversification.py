
import pytest
import pandas as pd
from analytics.diversification import calculate_average_correlation, calculate_concentration_ratio, calculate_correlation_matrix, calculate_effective_holdings, calculate_hhi, get_largest_position, get_position_weights


def test_get_position_weights():
    portfolio_values = {
        "AAPL": {"weight": 60},
        "MSFT": {"weight": 40},
    }

    result = get_position_weights(portfolio_values)

    assert result == {
        "AAPL": 60,
        "MSFT": 40,
    }

def test_get_largest_position():
    portfolio_values = {
        "AAPL": {"weight": 55},
        "MSFT": {"weight": 30},
        "NVDA": {"weight": 15},
    }

    result = get_largest_position(portfolio_values)

    assert result["ticker"] == "AAPL"
    assert result["weight"] == 55

def test_concentration_ratio():
    portfolio_values = {
        "AAPL": {"weight": 50},
        "MSFT": {"weight": 30},
        "NVDA": {"weight": 20},
    }

    result = calculate_concentration_ratio(
        portfolio_values,
        top_n=2
    )

    assert result == 80

def test_calculate_hhi():
    portfolio_values = {
        "AAPL": {"weight": 50},
        "MSFT": {"weight": 30},
        "NVDA": {"weight": 20},
    }

    result = calculate_hhi(portfolio_values)

    assert result == pytest.approx(0.38)

def test_effective_holdings():
    portfolio_values = {
        "AAPL": {"weight": 50},
        "MSFT": {"weight": 50},
    }

    result = calculate_effective_holdings(
        portfolio_values
    )

    assert result == pytest.approx(2.0)

def test_correlation_matrix():
    returns = pd.DataFrame({
        "AAPL": [0.01, 0.02, 0.03],
        "MSFT": [0.01, 0.02, 0.03],
    })

    result = calculate_correlation_matrix(
        returns
    )

    assert result.loc["AAPL", "MSFT"] == pytest.approx(1.0)

def test_average_correlation():
    returns = pd.DataFrame({
        "AAPL": [0.01, 0.02, 0.03],
        "MSFT": [0.01, 0.02, 0.03],
    })

    result = calculate_average_correlation(
        returns
    )

    assert result == pytest.approx(1.0)

