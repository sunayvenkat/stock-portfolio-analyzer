
import pytest
from analytics.valuation import (
    calculate_cost_basis,
    calculate_gain_loss,
    calculate_position_value,
    calculate_portfolio_value,
    calculate_position_weights,
    calculate_return_percentage
)


def test_calculate_position_value():
    result = calculate_position_value(10, 250)

    assert result == 2500

def test_calculate_portfolio_value():
    portfolio_values = {
        "AAPL": {
            "shares": 10,
            "current_price": 250,
            "current_value": 2500
        },
        "MSFT": {
            "shares": 5,
            "current_price": 500,
            "current_value": 2500
        }
    }

    assert calculate_portfolio_value(portfolio_values) == 5000

def test_calculate_cost_basis():
    assert calculate_cost_basis(10, 230) == 2300

def test_calculate_gain_loss():
    assert calculate_gain_loss(2500, 2300) == 200

def test_calculate_loss():
    assert calculate_gain_loss(2000, 2300) == -300

def test_calculate_return_percentage():
    result = calculate_return_percentage(2500, 2000)

    assert result == 25


def test_return_percentage_zero_cost_basis():
    with pytest.raises(ValueError):
        calculate_return_percentage(2500, 0)

def test_calculate_position_weights():
    portfolio_values = {
        "AAPL": {
            "current_value": 3000
        },
        "MSFT": {
            "current_value": 1000
        }
    }

    result = calculate_position_weights(portfolio_values)

    assert result["AAPL"]["weight"] == 75
    assert result["MSFT"]["weight"] == 25

def test_portfolio_weights_sum_to_100():
    portfolio_values = {
        "AAPL": {
            "current_value": 3000
        },
        "MSFT": {
            "current_value": 1000
        },
        "NVDA": {
            "current_value": 1000
        }
    }

    result = calculate_position_weights(portfolio_values)

    total_weight = sum(
        position["weight"]
        for position in result.values()
    )

    assert total_weight == pytest.approx(100)