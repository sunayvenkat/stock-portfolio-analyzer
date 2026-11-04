
import re
import threading
import time

import numpy as np
import pandas as pd
from yfinance.exceptions import YFRateLimitError

from models.portfolio import Portfolio

from data.market_data import get_closing_prices
from data.news_data import get_normalized_stock_news
from utils.logger import logger

from analytics.valuation import (
    get_portfolio_values,
    calculate_position_weights,
    calculate_total_cost_basis,
    calculate_portfolio_value,
    calculate_portfolio_gain_loss,
    calculate_portfolio_return,
)

from analytics.performance import (
    calculate_daily_returns,
    calculate_drawdown,
    calculate_portfolio_returns,
    analyze_portfolio_returns,
    analyze_performance,
)

from analytics.benchmark import compare_performance
from analytics.diversification import analyze_diversification

from analytics.optimization import (
    optimize_portfolio,
    calculate_expected_returns,
    calculate_covariance_matrix,
    calculate_expected_portfolio_return,
    calculate_portfolio_volatility,
)

from analytics.attribution import (
    calculate_stock_cumulative_returns,
    build_attribution_table,
)

from analytics.monte_carlo import (
    TRADING_DAYS,
    estimate_portfolio_parameters,
    run_monte_carlo,
    summarize_simulation,
    calculate_probability_of_loss,
    calculate_simulated_var,
)

from analytics.sentiment import (
    analyze_news_sentiment,
    summarize_sentiment,
)

from utils.constants import (
    DEFAULT_BENCHMARK,
    DEFAULT_PERIOD,
    DEFAULT_SIMULATIONS,
    DEFAULT_SIMULATION_YEARS,
)


TICKER_PATTERN = re.compile(r"^[A-Z0-9.\-^=]{1,12}$")
MAX_HOLDINGS = 25

#Paths x years per run: 10,000 x 252 days of float64 is about 20 MB, so a busy public server stays small
MAX_PATH_YEARS = 10_000

#Yahoo Finance rate-limits busy cloud addresses, so each ticker is fetched at most once per window and retried on a 429
CACHE_SECONDS = 600
RETRY_DELAYS = (2, 5)

_cache = {}
_cache_lock = threading.Lock()


def fetch_with_retries(fetch, ticker):
    for delay in RETRY_DELAYS:
        try:
            return fetch(ticker)
        except YFRateLimitError:
            logger.warning("Yahoo Finance rate limit hit; retrying in %ds", delay)
            time.sleep(delay)

    return fetch(ticker)

#Per-ticker cache, so its size is bounded by the tickers in use, never by portfolios; failures are not cached
def cached(kind, ticker, fetch):
    now = time.monotonic()

    with _cache_lock:
        hit = _cache.get((kind, ticker))

        if hit and now - hit[0] < CACHE_SECONDS:
            return hit[1]

    value = fetch_with_retries(fetch, ticker)

    with _cache_lock:
        for key in [key for key, (stamp, _) in _cache.items() if now - stamp >= CACHE_SECONDS]:
            del _cache[key]

        _cache[(kind, ticker)] = (now, value)

    return value


#Validates a ticker from the browser before it reaches Yahoo Finance
def parse_ticker(value):
    ticker = str(value).upper().strip()

    if not TICKER_PATTERN.match(ticker):
        raise ValueError(f"'{value}' is not a valid ticker symbol.")

    return ticker

#JSON numbers arrive as int or float; bool is excluded because it is an int in Python
def parse_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number.")

    if not np.isfinite(value):
        raise ValueError(f"{name} must be a finite number.")

    return float(value)

def parse_int_in_range(value, name, low, high):
    number = parse_number(value, name)

    if number != int(number) or not low <= number <= high:
        raise ValueError(f"{name} must be a whole number from {low} to {high}.")

    return int(number)

#Turns a dated pandas series into lists the browser can chart
def series_to_json(series):
    return {
        "dates": [date.strftime("%Y-%m-%d") for date in series.index],
        "values": [float(value) for value in series],
    }

def allocation_stats(weights, expected_returns, covariance_matrix):
    vector = np.array([weights[ticker] for ticker in expected_returns.index])

    expected_return = float(calculate_expected_portfolio_return(vector, expected_returns))
    volatility = float(calculate_portfolio_volatility(vector, covariance_matrix))

    return {
        "weights": {ticker: float(weight) for ticker, weight in weights.items()},
        "expected_return": expected_return,
        "volatility": volatility,
        "sharpe_ratio": expected_return / volatility if volatility else None,
    }

#Builds the portfolio from the browser's holdings and runs every analysis the dashboard shows
def analyze(payload):
    holdings = payload.get("holdings")

    if not isinstance(holdings, list) or not holdings:
        raise ValueError("Please enter at least one valid holding.")

    if len(holdings) > MAX_HOLDINGS:
        raise ValueError(f"A portfolio can hold at most {MAX_HOLDINGS} positions.")

    portfolio = Portfolio("Web Portfolio")

    for row in holdings:
        if not isinstance(row, dict):
            raise TypeError("Each holding must have a ticker, shares and purchase price.")

        portfolio.add_position(
            parse_ticker(row.get("ticker", "")),
            parse_number(row.get("shares"), "Shares"),
            parse_number(row.get("purchase_price"), "Purchase price"),
        )

    tickers = list(portfolio.positions.keys())

    #One history request per ticker (dict.fromkeys keeps SPY once if it is also held); the latest close is the current price
    closes = {
        ticker: cached("prices", ticker, lambda symbol: get_closing_prices(symbol, period=DEFAULT_PERIOD))
        for ticker in dict.fromkeys(tickers + [DEFAULT_BENCHMARK])
    }

    values = calculate_position_weights(
        get_portfolio_values(portfolio, get_price=lambda ticker: float(closes[ticker].iloc[-1]))
    )

    #Holdings and benchmark on the dates they share, as get_multiple_closing_prices does
    all_prices = pd.DataFrame(closes).dropna()

    benchmark_prices = all_prices[DEFAULT_BENCHMARK]
    historical_prices = all_prices[tickers]

    stock_returns = calculate_daily_returns(historical_prices)

    weights = {
        ticker: data["weight"] / 100
        for ticker, data in values.items()
    }

    portfolio_returns = calculate_portfolio_returns(stock_returns, weights)

    performance = analyze_portfolio_returns(portfolio_returns)
    benchmark_metrics = analyze_performance(benchmark_prices)

    #Growth of $1 for both, starting from the first shared date
    portfolio_growth = (1 + portfolio_returns).cumprod().reindex(historical_prices.index).fillna(1.0)
    benchmark_growth = benchmark_prices / benchmark_prices.iloc[0]

    attribution = build_attribution_table(
        values,
        calculate_stock_cumulative_returns(historical_prices),
    )

    diversification = None
    optimization = None

    if len(tickers) >= 2:
        result = analyze_diversification(values, stock_returns)

        correlation = result["correlation_matrix"]

        diversification = {
            **{key: value for key, value in result.items() if key != "correlation_matrix"},
            "correlation_matrix": {
                "tickers": list(correlation.columns),
                "values": correlation.values.tolist(),
            },
        }

        expected_returns = calculate_expected_returns(stock_returns)
        covariance_matrix = calculate_covariance_matrix(stock_returns)

        try:
            optimized = optimize_portfolio(stock_returns)

            optimization = {
                name: allocation_stats(allocation, expected_returns, covariance_matrix)
                for name, allocation in [("current", weights), *optimized.items()]
            }
        except ValueError:
            optimization = None

    expected_return, volatility = estimate_portfolio_parameters(portfolio_returns)
    total_value = calculate_portfolio_value(values)

    return {
        "as_of": historical_prices.index[-1].strftime("%Y-%m-%d"),
        "benchmark": DEFAULT_BENCHMARK,
        "summary": {
            "cost_basis": calculate_total_cost_basis(values),
            "current_value": total_value,
            "gain_loss": calculate_portfolio_gain_loss(values),
            "return_percentage": calculate_portfolio_return(values),
        },
        "holdings": values,
        "growth": {
            "dates": series_to_json(portfolio_growth)["dates"],
            "portfolio": [float(value) for value in portfolio_growth],
            "benchmark": [float(value) for value in benchmark_growth],
        },
        "drawdown": series_to_json(calculate_drawdown(portfolio_growth)),
        "performance": performance,
        "comparison": compare_performance(performance, benchmark_metrics),
        "attribution": attribution,
        "diversification": diversification,
        "optimization": optimization,
        "stocks": {
            ticker: {
                "prices": series_to_json(historical_prices[ticker]),
                "drawdown": [float(value) for value in calculate_drawdown(historical_prices[ticker])],
                "metrics": analyze_performance(historical_prices[ticker]),
            }
            for ticker in tickers
        },
        "simulation_params": {
            "expected_return": float(expected_return),
            "volatility": float(volatility),
        },
        "simulation": simulate({
            "expected_return": float(expected_return),
            "volatility": float(volatility),
            "initial_value": total_value,
            "simulations": DEFAULT_SIMULATIONS,
            "years": DEFAULT_SIMULATION_YEARS,
        }),
    }

#Runs the Monte Carlo simulation and condenses the paths into percentile bands and a histogram
def simulate(payload):
    expected_return = parse_number(payload.get("expected_return"), "Expected return")
    volatility = parse_number(payload.get("volatility"), "Volatility")
    initial_value = parse_number(payload.get("initial_value"), "Initial value")
    simulations = parse_int_in_range(payload.get("simulations"), "Simulations", 100, 10000)
    years = parse_int_in_range(payload.get("years"), "Years", 1, 10)

    if simulations * years > MAX_PATH_YEARS:
        raise ValueError(f"A {years}-year horizon allows at most {MAX_PATH_YEARS // years:,} simulations.")

    if volatility < 0 or initial_value <= 0:
        raise ValueError("Volatility and initial value must be positive.")

    days = years * TRADING_DAYS

    paths = run_monte_carlo(
        expected_return=expected_return,
        volatility=volatility,
        simulations=simulations,
        days=days,
        initial_value=initial_value,
    )

    #About 120 points per band is plenty for a chart; the last day is always kept
    step = max(1, days // 120)
    rows = sorted(set(range(step - 1, days, step)) | {days - 1})

    percentiles = [0.05, 0.5, 0.95]
    bands = paths.iloc[rows].quantile(percentiles, axis=1)

    counts, edges = np.histogram(paths.iloc[-1], bins=30)

    return {
        "simulations": simulations,
        "years": years,
        "initial_value": initial_value,
        "days": [0] + [row + 1 for row in rows],
        "bands": {
            f"p{round(p * 100)}": [initial_value] + [float(v) for v in bands.loc[p]]
            for p in percentiles
        },
        "summary": summarize_simulation(paths),
        "probability_of_loss": float(calculate_probability_of_loss(paths, initial_value)),
        "value_at_risk": calculate_simulated_var(paths, initial_value),
        "histogram": {
            "counts": counts.tolist(),
            "edges": edges.tolist(),
        },
    }

#Recent headlines for one holding, scored with VADER
def news(payload):
    articles = analyze_news_sentiment(
        cached("news", parse_ticker(payload.get("ticker", "")), get_normalized_stock_news)[:10]
    )

    return {
        "articles": articles,
        "summary": summarize_sentiment(articles),
    }
