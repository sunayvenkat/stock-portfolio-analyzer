

import streamlit as st
from models.portfolio import Portfolio
import pandas as pd

from analytics.valuation import (
    get_portfolio_values,
    calculate_position_weights,
    calculate_total_cost_basis,
    calculate_portfolio_value,
    calculate_portfolio_gain_loss,
    calculate_portfolio_return,
)

from data.market_data import (
    get_multiple_closing_prices,
)

from analytics.performance import (
    calculate_daily_returns,
    calculate_portfolio_returns,
    analyze_portfolio_returns,
)

from analytics.performance import (
    analyze_performance,
)

from analytics.benchmark import (
    compare_performance,
)

from analytics.diversification import (
    analyze_diversification,
)


#Creates a Streamlit app for analyzing stock portfolios
st.set_page_config(
    page_title="Portfolio Analyzer",
    page_icon="📈",
    layout="wide"
)

st.title("Stock Portfolio Analyzer")

#Header
st.sidebar.header("Portfolio Input")

#Takes in input for the stock ticker, number of shares, and purchase price
default_holdings = pd.DataFrame({
    "Ticker": ["AAPL", "MSFT", "NVDA"],
    "Shares": [10.0, 5.0, 8.0],
    "Purchase Price": [230.0, 400.0, 180.0],
})

edited_holdings = st.sidebar.data_editor(
    default_holdings,
    num_rows="dynamic",
    use_container_width=True,
)

analyze_button = st.sidebar.button("Analyze Portfolio")

if analyze_button:
    try:
        portfolio = Portfolio("Dashboard Portfolio")

        for _, row in edited_holdings.iterrows():
            ticker = str(row["Ticker"]).strip()

            if not ticker:
                continue

            portfolio.add_position(
                ticker,
                float(row["Shares"]),
                float(row["Purchase Price"])
            )

        if not portfolio.positions:
            raise ValueError(
                "Please enter at least one valid holding."
            )

        values = get_portfolio_values(portfolio)

        values = calculate_position_weights(values)

        total_cost = calculate_total_cost_basis(values)

        total_value = calculate_portfolio_value(values)

        total_gain = calculate_portfolio_gain_loss(values)

        total_return = calculate_portfolio_return(values)

        #Displays summary metrics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Cost Basis",
            f"${total_cost:,.2f}"
        )

        col2.metric(
            "Current Value",
            f"${total_value:,.2f}"
        )

        col3.metric(
            "Gain / Loss",
            f"${total_gain:,.2f}"
        )

        col4.metric(
            "Return",
            f"{total_return:.2f}%"
        )

        holdings_data = []

        for ticker, data in values.items():
            holdings_data.append({
                "Ticker": ticker,
                "Shares": data["shares"],
                "Purchase Price": data["purchase_price"],
                "Current Price": data["current_price"],
                "Cost Basis": data["cost_basis"],
                "Current Value": data["current_value"],
                "Gain/Loss": data["gain_loss"],
                "Return %": data["return_percentage"],
                "Weight %": data["weight"],
            })

        holdings_df = pd.DataFrame(holdings_data)

        st.subheader("Portfolio Holdings")

        st.dataframe(
            holdings_df,
            use_container_width=True
        )

        tickers = list(portfolio.positions.keys())

        historical_prices = (get_multiple_closing_prices(tickers,period="1y"))

        stock_returns = calculate_daily_returns(historical_prices)

        weights = {
            ticker: data["weight"] / 100
            for ticker, data in values.items()
        }

        portfolio_returns = calculate_portfolio_returns(stock_returns,weights)

        performance = analyze_portfolio_returns(portfolio_returns)

        st.subheader(
            "Historical Performance"
        )

        p1, p2, p3, p4 = st.columns(4)

        p1.metric(
            "1Y Return",
            f"{performance['cumulative_return']:.2%}"
        )

        p2.metric(
            "Volatility",
            f"{performance['annualized_volatility']:.2%}"
        )

        p3.metric(
            "Sharpe Ratio",
            f"{performance['sharpe_ratio']:.2f}"
        )

        p4.metric(
            "Max Drawdown",
            f"{performance['max_drawdown']:.2%}"
        )

        portfolio_growth = (1 + portfolio_returns).cumprod()

        st.subheader(
            "Portfolio Growth"
        )

        st.line_chart(
            portfolio_growth
        )

        all_tickers = tickers + ["SPY"]

        all_prices = get_multiple_closing_prices(all_tickers,period="1y")

        benchmark_prices = all_prices["SPY"]

        historical_prices = all_prices.drop(columns=["SPY"])

        benchmark_metrics = analyze_performance(benchmark_prices)

        comparison = compare_performance(performance,benchmark_metrics)

        st.subheader(
            "Portfolio vs S&P 500"
        )

        b1, b2, b3 = st.columns(3)

        b1.metric(
            "Portfolio Return",
            f"{comparison['portfolio_return']:.2%}"
        )

        b2.metric(
            "SPY Return",
            f"{comparison['benchmark_return']:.2%}"
        )

        b3.metric(
            "Excess Return",
            f"{comparison['excess_return']:.2%}"
        )

        if len(portfolio.positions) >= 2:
            diversification = (analyze_diversification(values, stock_returns))

            # display diversification
        else:
            st.info(
                "Add at least two holdings "
                "to view diversification metrics."
            )

        diversification = analyze_diversification(values, stock_returns)

        st.subheader(
            "Diversification"
        )

        d1, d2, d3, d4 = st.columns(4)

        d1.metric(
            "Holdings",
            diversification["number_of_holdings"]
        )

        d2.metric(
            "Largest Position",
            diversification["largest_position"]["ticker"]
        )

        d3.metric(
            "Effective Holdings",
            f"{diversification['effective_holdings']:.2f}"
        )

        d4.metric(
            "Average Correlation",
            f"{diversification['average_correlation']:.2f}"
        )

        st.write(
            "Correlation Matrix"
        )

        st.dataframe(
            diversification[
                "correlation_matrix"
            ]
        )
    except Exception as error:
        st.error(
            f"Unable to analyze portfolio: {error}"
        )

    




