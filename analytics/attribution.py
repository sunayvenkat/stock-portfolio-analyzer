

#Finds the contributions rates of each stock, based on weightage in portfolio and its returns
def calculate_return_contribution(
    portfolio_values,
    stock_returns
):
    contributions = {}

    for ticker, data in portfolio_values.items():
        weight = data["weight"] / 100

        if ticker not in stock_returns:
            raise ValueError(
                f"Missing return for ticker: {ticker}"
            )

        contribution = (
            weight * stock_returns[ticker]
        )

        contributions[ticker] = contribution

    return contributions

#Calculates each stock's cumulative return
def calculate_stock_cumulative_returns(
    historical_prices
):
    returns = {}

    for ticker in historical_prices.columns:
        prices = historical_prices[ticker]

        cumulative_return = (
            prices.iloc[-1]
            / prices.iloc[0]
        ) - 1

        returns[ticker] = cumulative_return

    return returns

#Ranked attribution table
def build_attribution_table(
    portfolio_values,
    stock_returns
):
    rows = []

    contributions = calculate_return_contribution(
        portfolio_values,
        stock_returns
    )

    for ticker, data in portfolio_values.items():
        rows.append({
            "Ticker": ticker,
            "Weight": data["weight"],
            "Stock Return": stock_returns[ticker],
            "Contribution": contributions[ticker],
        })

    return sorted(
        rows,
        key=lambda row: row["Contribution"],
        reverse=True
    )

