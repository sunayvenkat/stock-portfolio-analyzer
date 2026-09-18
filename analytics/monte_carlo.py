

import numpy as np
import pandas as pd


TRADING_DAYS = 252

#Simulates growth of a stock over a period
def simulate_portfolio_path(
    expected_return,
    volatility,
    days=TRADING_DAYS,
    initial_value=10000,
    random_state=None
):
    rng = np.random.default_rng(random_state)

    daily_return = expected_return / TRADING_DAYS
    daily_volatility = volatility / np.sqrt(TRADING_DAYS)

    simulated_returns = rng.normal(
        loc=daily_return,
        scale=daily_volatility,
        size=days
    )

    growth = np.cumprod(
        1 + simulated_returns
    )

    return initial_value * growth

#Runs the simulation multiple times to create a distribution of possible outcomes
def run_monte_carlo(
    expected_return,
    volatility,
    simulations=1000,
    days=TRADING_DAYS,
    initial_value=10000,
    random_state=None
):
    rng = np.random.default_rng(random_state)

    paths = np.zeros(
        (days, simulations)
    )

    daily_return = expected_return / TRADING_DAYS
    daily_volatility = volatility / np.sqrt(TRADING_DAYS)

    for simulation in range(simulations):
        simulated_returns = rng.normal(
            loc=daily_return,
            scale=daily_volatility,
            size=days
        )

        growth = np.cumprod(
            1 + simulated_returns
        )

        paths[:, simulation] = (
            initial_value * growth
        )

    return pd.DataFrame(paths)

#Estimate portfolio parameters
def estimate_portfolio_parameters(
    portfolio_returns
):
    annual_return = (
        portfolio_returns.mean()
        * TRADING_DAYS
    )

    annual_volatility = (
        portfolio_returns.std()
        * np.sqrt(TRADING_DAYS)
    )

    return annual_return, annual_volatility

def summarize_simulation(simulations):
    final_values = simulations.iloc[-1]

    return {
        "mean": float(final_values.mean()),
        "median": float(final_values.median()),
        "minimum": float(final_values.min()),
        "maximum": float(final_values.max()),
        "percentile_5": float(final_values.quantile(0.05)),
        "percentile_95": float(final_values.quantile(0.95)),
    }

def calculate_probability_of_loss(
    simulations,
    initial_value
):
    final_values = simulations.iloc[-1]

    losses = (
        final_values < initial_value
    )

    return float(losses.mean())

def calculate_probability_of_loss(
    simulations,
    initial_value
):
    final_values = simulations.iloc[-1]

    losses = (
        final_values < initial_value
    )

    return losses.mean()

def calculate_simulated_var(
    simulations,
    initial_value,
    confidence_level=0.95
):
    final_values = simulations.iloc[-1]

    percentile = 1 - confidence_level

    cutoff = final_values.quantile(
        percentile
    )

    return float(initial_value - cutoff)