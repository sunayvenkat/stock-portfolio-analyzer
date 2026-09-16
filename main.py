

from data.market_data import get_historical_prices, get_multiple_closing_prices
from models.portfolio import Portfolio
from analytics.valuation import (
    calculate_portfolio_gain_loss,
    calculate_portfolio_return,
    calculate_position_weights,
    calculate_total_cost_basis,
    get_portfolio_values,
    calculate_portfolio_value
)


portfolio = Portfolio("My Portfolio")

portfolio.add_position("AAPL", 10, 230)
portfolio.add_position("MSFT", 5, 400)
portfolio.add_position("NVDA", 8, 180)


values = get_portfolio_values(portfolio)
values = calculate_position_weights(values)

total_value = calculate_portfolio_value(values)


for ticker, data in values.items():
    print(
        f"{ticker}: "
        f"{data['shares']} shares x "
        f"${data['current_price']:.2f} = "
        f"${data['current_value']:,.2f}"
    )


print("-" * 40)

print(f"Portfolio Value: ${total_value:,.2f}")

total_cost = calculate_total_cost_basis(values)
total_value = calculate_portfolio_value(values)
total_gain = calculate_portfolio_gain_loss(values)
total_return = calculate_portfolio_return(values)

for ticker, data in values.items():
    print(f"\n{ticker}")
    print(f"Shares: {data['shares']}")
    print(f"Purchase Price: ${data['purchase_price']:.2f}")
    print(f"Current Price: ${data['current_price']:.2f}")
    print(f"Cost Basis: ${data['cost_basis']:,.2f}")
    print(f"Current Value: ${data['current_value']:,.2f}")
    print(f"Gain/Loss: ${data['gain_loss']:,.2f}")
    print(f"Return: {data['return_percentage']:.2f}%")
    print(f"Portfolio Weight: {data['weight']:.2f}%")

print("\n" + "=" * 40)
print("PORTFOLIO SUMMARY")
print("=" * 40)

print(f"Cost Basis: ${total_cost:,.2f}")
print(f"Current Value: ${total_value:,.2f}")
print(f"Gain/Loss: ${total_gain:,.2f}")
print(f"Return: {total_return:.2f}%")


prices = get_multiple_closing_prices(
    ["AAPL", "MSFT", "NVDA"],
    period="1y"
)

print(prices.head())