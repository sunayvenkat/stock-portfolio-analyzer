
import pandas as pd
import pytest

from analytics.attribution import (
    calculate_return_contribution,
    calculate_stock_cumulative_returns,
)


def test_return_contribution():
    portfolio_values = {
        "AAPL": {"weight": 60},
        "MSFT": {"weight": 40},
    }

    stock_returns = {
        "AAPL": 0.10,
        "MSFT": 0.05,
    }

    result = calculate_return_contribution(
        portfolio_values,
        stock_returns
    )

    assert result["AAPL"] == pytest.approx(0.06)
    assert result["MSFT"] == pytest.approx(0.02)

def test_stock_cumulative_returns():
    prices = pd.DataFrame({
        "AAPL": [100, 110],
        "MSFT": [200, 220],
    })

    result = calculate_stock_cumulative_returns(
        prices
    )

    assert result["AAPL"] == pytest.approx(0.10)
    assert result["MSFT"] == pytest.approx(0.10)

