
import numpy as np

#Retrieves the weights of each position based on portfolio values
def get_position_weights(portfolio_values):
    return {
        ticker: data["weight"]
        for ticker, data in portfolio_values.items()
    }

#Returns the largest position in the portfolio based on weights
def get_largest_position(portfolio_values):
    if not portfolio_values:
        raise ValueError("Portfolio cannot be empty.")

    ticker = max(
        portfolio_values,
        key=lambda ticker: portfolio_values[ticker]["weight"]
    )

    return {
        "ticker": ticker,
        "weight": portfolio_values[ticker]["weight"]
    }

#Finds the concentration ratio of the portfolio based on the largest position
def calculate_concentration_ratio(
    portfolio_values,
    top_n=3
):
    if top_n <= 0:
        raise ValueError("top_n must be greater than zero.")

    weights = sorted(
        [
            data["weight"]
            for data in portfolio_values.values()
        ],
        reverse=True
    )

    return sum(weights[:top_n])

#Calculates the HHI (closer to 1, more concentrated, closer to 0, more diversified)
def calculate_hhi(portfolio_values):
    weights = [
        data["weight"] / 100
        for data in portfolio_values.values()
    ]

    return sum(
        weight ** 2
        for weight in weights
    )

#Calculates effective holdings
def calculate_effective_holdings(portfolio_values):
    hhi = calculate_hhi(portfolio_values)

    if hhi == 0:
        raise ValueError("HHI cannot be zero.")

    return 1 / hhi

#Creates a correlation matrix of the portfolio based on historical prices
def calculate_correlation_matrix(returns):
    return returns.corr()

#Creates a pairwise correlation matrix of the portfolio based on historical prices
def calculate_average_correlation(returns):
    correlation_matrix = (
        calculate_correlation_matrix(returns)
    )

    if len(correlation_matrix.columns) < 2:
        raise ValueError(
            "At least two assets are required."
        )

    mask = np.triu(
        np.ones(
            correlation_matrix.shape,
            dtype=bool
        ),
        k=1
    )

    correlations = correlation_matrix.where(
        mask
    ).stack()

    return correlations.mean()

#Combine all the metrics
def analyze_diversification(
    portfolio_values,
    returns
):
    largest_position = get_largest_position(
        portfolio_values
    )

    return {
        "number_of_holdings":
            len(portfolio_values),

        "largest_position":
            largest_position,

        "top_3_concentration":
            calculate_concentration_ratio(
                portfolio_values,
                top_n=3
            ),

        "hhi":
            calculate_hhi(
                portfolio_values
            ),

        "effective_holdings":
            calculate_effective_holdings(
                portfolio_values
            ),

        "average_correlation":
            calculate_average_correlation(
                returns
            ),

        "correlation_matrix":
            calculate_correlation_matrix(
                returns
            ),
    }