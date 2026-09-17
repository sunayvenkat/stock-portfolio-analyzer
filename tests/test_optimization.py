

import numpy as np
import pandas as pd
import pytest

from analytics.optimization import (
    calculate_expected_returns,
    calculate_covariance_matrix,
    calculate_expected_portfolio_return,
    calculate_portfolio_volatility,
    find_minimum_volatility_portfolio,
)

def test_expected_portfolio_return():
    weights = np.array([
        0.60,
        0.40
    ])

    expected_returns = np.array([
        0.10,
        0.20
    ])

    result = calculate_expected_portfolio_return(
        weights,
        expected_returns
    )

    assert result == pytest.approx(
        0.14
    )

def test_minimum_volatility_weights_sum_to_one():
    expected_returns = np.array([
        0.10,
        0.15
    ])

    covariance_matrix = np.array([
        [0.04, 0.01],
        [0.01, 0.09]
    ])

    weights = (
        find_minimum_volatility_portfolio(
            expected_returns,
            covariance_matrix
        )
    )

    assert sum(weights) == pytest.approx(
        1.0
    )

def test_minimum_volatility_weights_sum_to_one():
    expected_returns = np.array([
        0.10,
        0.15
    ])

    covariance_matrix = np.array([
        [0.04, 0.01],
        [0.01, 0.09]
    ])

    weights = (
        find_minimum_volatility_portfolio(
            expected_returns,
            covariance_matrix
        )
    )

    assert sum(weights) == pytest.approx(
        1.0
    )

    assert all(
        weight >= 0
        for weight in weights
    )

