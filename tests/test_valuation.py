
from analytics.valuation import (
    calculate_position_value,
    calculate_portfolio_value
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