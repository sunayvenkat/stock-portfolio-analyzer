

from data.market_data import get_closing_prices
from analytics.performance import (
    calculate_daily_returns,
    analyze_performance,
)

#Pulls data from the S&P 500 for comparison
def get_benchmark_prices(benchmark="SPY", period="1y"):
    return get_closing_prices(benchmark, period=period)

#Analyzes the performance of the benchmark
def analyze_benchmark(
    benchmark="SPY",
    period="1y"
):
    prices = get_benchmark_prices(
        benchmark,
        period
    )

    return analyze_performance(prices)

def calculate_excess_return(
    portfolio_return,
    benchmark_return
):
    return portfolio_return - benchmark_return

def compare_performance(
    portfolio_metrics,
    benchmark_metrics
):
    return {
        "portfolio_return":
            portfolio_metrics["cumulative_return"],

        "benchmark_return":
            benchmark_metrics["cumulative_return"],

        "excess_return":
            calculate_excess_return(
                portfolio_metrics["cumulative_return"],
                benchmark_metrics["cumulative_return"]
            ),

        "portfolio_volatility":
            portfolio_metrics["annualized_volatility"],

        "benchmark_volatility":
            benchmark_metrics["annualized_volatility"],

        "portfolio_sharpe":
            portfolio_metrics["sharpe_ratio"],

        "benchmark_sharpe":
            benchmark_metrics["sharpe_ratio"],

        "portfolio_max_drawdown":
            portfolio_metrics["max_drawdown"],

        "benchmark_max_drawdown":
            benchmark_metrics["max_drawdown"],
    }

