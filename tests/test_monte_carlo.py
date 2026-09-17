

import pytest

from analytics.monte_carlo import (
    simulate_portfolio_path,
    run_monte_carlo,
    summarize_simulation,
    calculate_probability_of_loss,
)

def test_monte_carlo_dimensions():
    result = run_monte_carlo(
        expected_return=0.10,
        volatility=0.20,
        simulations=500,
        days=100,
        random_state=42
    )

    assert result.shape == (
        100,
        500
    )

def test_simulated_path_length():
    path = simulate_portfolio_path(
        expected_return=0.10,
        volatility=0.20,
        days=100,
        random_state=42
    )

    assert len(path) == 100

def test_monte_carlo_dimensions():
    result = run_monte_carlo(
        expected_return=0.10,
        volatility=0.20,
        simulations=500,
        days=100,
        random_state=42
    )

    assert result.shape == (
        100,
        500
    )

