
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

#Returns a dictionary containing the current value of each position in the portfolio
def get_portfolio_values(portfolio):
    values = {}

    for ticker, position in portfolio.positions.items():
        shares = position["shares"]
        purchase_price = position["purchase_price"]
        current_price = get_current_price(ticker)

        position_value = calculate_position_value(shares, current_price)

        cost_basis = calculate_cost_basis(shares, purchase_price)

        gain_loss = calculate_gain_loss(position_value, cost_basis)

        return_percentage = calculate_return_percentage(position_value, cost_basis)

        values[ticker] = {
            "shares": shares,
            "purchase_price": purchase_price,
            "current_price": current_price,
            "cost_basis": cost_basis,
            "gain_loss": gain_loss,
            "current_value": position_value,
            "return_percentage": return_percentage
        }

    return values

#Returns total portfolio value
def calculate_portfolio_value(portfolio_values):
    total_value = 0

    for position in portfolio_values.values():
        total_value += position["current_value"]

    return total_value

#Returns cost basis for a given position
def calculate_cost_basis(shares, purchase_price):
    return shares * purchase_price

#Returns gain or loss for a given position
def calculate_gain_loss(current_value, cost_basis):
    return current_value - cost_basis

#Returns percentage return given current value and cost basis
def calculate_return_percentage(current_value, cost_basis):
    if cost_basis == 0:
        raise ValueError("Cost basis cannot be zero.")

    return ((current_value - cost_basis) / cost_basis) * 100

#Calculates position weights; which stocks are more heavily invested in than others
def calculate_position_weights(portfolio_values):
    total_value = calculate_portfolio_value(portfolio_values)

    if total_value == 0:
        raise ValueError("Portfolio value cannot be zero.")

    for position in portfolio_values.values():
        position["weight"] = (position["current_value"] / total_value) * 100

    return portfolio_values

#Calculates performace of the entire portfolio
def calculate_total_cost_basis(portfolio_values):
    return sum(
        position["cost_basis"]
        for position in portfolio_values.values()
    )

def calculate_portfolio_gain_loss(portfolio_values):
    current_value = calculate_portfolio_value(portfolio_values)
    cost_basis = calculate_total_cost_basis(portfolio_values)

    return current_value - cost_basis

def calculate_portfolio_return(portfolio_values):
    current_value = calculate_portfolio_value(portfolio_values)
    cost_basis = calculate_total_cost_basis(portfolio_values)

    return calculate_return_percentage(current_value, cost_basis)

