
from data.market_data import get_current_price

def calculate_position_value(shares, current_price):
    return shares * current_price

def calculate_portfolio_value(portfolio):
    total_value = 0

    #Iterates through all positions in the portfolio, calculating the total value based on current market prices
    for ticker, position in portfolio.get_all_positions().items():

        current_price = get_current_price(ticker)

        total_value += calculate_position_value(position['shares'], current_price)

    return total_value

def get_portfolio_values(portfolio):
    values = {}

    for ticker, position in portfolio.positions.items():
        shares = position["shares"]
        current_price = get_current_price(ticker)

        position_value = calculate_position_value(
            shares,
            current_price
        )

        values[ticker] = {
            "shares": shares,
            "current_price": current_price,
            "current_value": position_value
        }

    return values

def calculate_portfolio_value(portfolio_values):
    total_value = 0

    for position in portfolio_values.values():
        total_value += position["current_value"]

    return total_value