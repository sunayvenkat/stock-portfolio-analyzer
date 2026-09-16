

import pytest

from analytics.benchmark import (
    calculate_excess_return,
    compare_performance,
)


def test_calculate_excess_return():
    result = calculate_excess_return(
        0.15,
        0.10
    )

    assert result == pytest.approx(0.05)


def test_compare_performance():
    portfolio_metrics = {
        "cumulative_return": 0.15,
        "annualized_volatility": 0.20,
        "sharpe_ratio": 0.75,
        "max_drawdown": -0.12,
    }

    benchmark_metrics = {
        "cumulative_return": 0.10,
        "annualized_volatility": 0.15,
        "sharpe_ratio": 0.67,
        "max_drawdown": -0.08,
    }

    result = compare_performance(
        portfolio_metrics,
        benchmark_metrics
    )

    assert result["portfolio_return"] == 0.15
    assert result["benchmark_return"] == 0.10
    assert result["excess_return"] == pytest.approx(0.05)

    assert result["portfolio_volatility"] == 0.20
    assert result["benchmark_volatility"] == 0.15

    assert result["portfolio_sharpe"] == 0.75
    assert result["benchmark_sharpe"] == 0.67

    assert result["portfolio_max_drawdown"] == -0.12
    assert result["benchmark_max_drawdown"] == -0.08