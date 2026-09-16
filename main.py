

from models.portfolio import Portfolio
from analytics.valuation import (
    get_portfolio_values,
    calculate_portfolio_value
)


portfolio = Portfolio("My Portfolio")

portfolio.add_position("AAPL", 10, 230)
portfolio.add_position("MSFT", 5, 400)
portfolio.add_position("NVDA", 8, 180)


values = get_portfolio_values(portfolio)

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