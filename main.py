
from models.portfolio import Portfolio

portfolio = Portfolio("My Portfolio")

portfolio.add_position("AAPL", 10, 230)
portfolio.add_position("NVDA", 5, 180)
portfolio.add_position("MSFT", 3, 500)

print(portfolio.get_position("AAPL"))
print(portfolio.get_all_positions())
print(portfolio.total_cost())

