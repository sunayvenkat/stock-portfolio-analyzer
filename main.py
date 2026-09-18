

from analytics import diversification
from analytics.diversification import (analyze_diversification, )
from analytics.benchmark import analyze_benchmark, compare_performance
from analytics.performance import analyze_performance, analyze_portfolio_returns, calculate_daily_returns, calculate_portfolio_returns
from data.market_data import get_closing_prices, get_historical_prices, get_multiple_closing_prices
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

#Summary of the portfolio
total_cost = calculate_total_cost_basis(values)
total_value = calculate_portfolio_value(values)
total_gain = calculate_portfolio_gain_loss(values)
total_return = calculate_portfolio_return(values)

#Print individual positions
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

#Print current portfolio summary
print("\n" + "=" * 40)
print("PORTFOLIO SUMMARY")
print("=" * 40)

print(f"Cost Basis: ${total_cost:,.2f}")
print(f"Current Value: ${total_value:,.2f}")
print(f"Gain/Loss: ${total_gain:,.2f}")
print(f"Return: {total_return:.2f}%")

#Convert weights to decimals
weights = {
    ticker: data["weight"] / 100
    for ticker, data in values.items()
}

#Get historical prices
tickers = list(portfolio.positions.keys())


#Gets the prices of stocks + benchmark at the same time, for accurate dates
all_prices = get_multiple_closing_prices(tickers + ["SPY"], period="1y")


#Splits into their own respective categories for analysis
benchmark_prices = all_prices["SPY"]
historical_prices = all_prices.drop(columns=["SPY"])


#Calculate stock returns
stock_returns = calculate_daily_returns(historical_prices)


#Calculate portfolio returns
portfolio_returns = calculate_portfolio_returns(stock_returns, weights)


#Analyze historical performance
portfolio_metrics = analyze_portfolio_returns(portfolio_returns)


#Analyze benchmark performance
benchmark_metrics = analyze_performance(benchmark_prices)


#Compares the performance of the two
comparison = compare_performance(portfolio_metrics, benchmark_metrics)


print("\n" + "=" * 50)
print("PORTFOLIO VS BENCHMARK")
print("=" * 50)

print(
    f"Portfolio Return: "
    f"{comparison['portfolio_return']:.2%}"
)

print(
    f"SPY Return: "
    f"{comparison['benchmark_return']:.2%}"
)

print(
    f"Excess Return: "
    f"{comparison['excess_return']:.2%}"
)

print()
print(
    f"Portfolio Volatility: "
    f"{comparison['portfolio_volatility']:.2%}"
)

print(
    f"SPY Volatility: "
    f"{comparison['benchmark_volatility']:.2%}"
)

print()
print(
    f"Portfolio Sharpe: "
    f"{comparison['portfolio_sharpe']:.2f}"
)

print(
    f"SPY Sharpe: "
    f"{comparison['benchmark_sharpe']:.2f}"
)

print()
print(
    f"Portfolio Max Drawdown: "
    f"{comparison['portfolio_max_drawdown']:.2%}"
)

print(
    f"SPY Max Drawdown: "
    f"{comparison['benchmark_max_drawdown']:.2%}"
)

#Print historical performance 
print("\n" + "=" * 40)
print("HISTORICAL PORTFOLIO PERFORMANCE")
print("=" * 40)

print("Cumulative Returns: " + f"{portfolio_metrics['cumulative_return']:.2%}")
print("Annualized Volatility: " + f"{portfolio_metrics['annualized_volatility']:.2%}")
print("Sharpe Ratio: " + f"{portfolio_metrics['sharpe_ratio']:.2f}")
print("Max Drawdown: " + f"{portfolio_metrics['max_drawdown']:.2%}")

#Calculates how diversified the portfolio is
diversification = analyze_diversification(
    values,
    stock_returns
)

#Displays diversification
print("\n" + "=" * 50)
print("DIVERSIFICATION ANALYSIS")
print("=" * 50)

print(
    f"Number of Holdings: "
    f"{diversification['number_of_holdings']}"
)

print(
    f"Largest Holding: "
    f"{diversification['largest_position']['ticker']}"
)

print(
    f"Largest Holding Weight: "
    f"{diversification['largest_position']['weight']:.2f}%"
)

print(
    f"Top 3 Concentration: "
    f"{diversification['top_3_concentration']:.2f}%"
)

print(
    f"HHI: "
    f"{diversification['hhi']:.3f}"
)

print(
    f"Effective Holdings: "
    f"{diversification['effective_holdings']:.2f}"
)

print(
    f"Average Correlation: "
    f"{diversification['average_correlation']:.2f}"
)

print("\nCORRELATION MATRIX")

print(
    diversification[
        "correlation_matrix"
    ].round(2)
)


from data.news_data import get_stock_news


news = get_stock_news("AAPL")

for article in news[:5]:
    print(article)