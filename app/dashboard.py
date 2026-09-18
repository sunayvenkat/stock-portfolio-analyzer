
import os
import sys

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


import streamlit as st
from analytics.monte_carlo import estimate_portfolio_parameters
from models.portfolio import Portfolio
import pandas as pd

from data.news_data import (
    get_normalized_stock_news,
)

from analytics.sentiment import (
    analyze_news_sentiment,
    summarize_sentiment,
)

from analytics.monte_carlo import (
    estimate_portfolio_parameters,
    run_monte_carlo,
    estimate_portfolio_parameters,
    summarize_simulation,
    calculate_probability_of_loss,
    calculate_simulated_var,
)

from analytics.optimization import (
    optimize_portfolio,
)

from analytics.attribution import (
    calculate_stock_cumulative_returns,
    build_attribution_table,
)

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
    calculate_drawdown,
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

if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

analyze_button = st.sidebar.button("Analyze Portfolio")

if analyze_button:
    st.session_state.analyzed = True

if st.session_state.analyzed:
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
            raise ValueError("Please enter at least one valid holding.")

        values = get_portfolio_values(portfolio)

        values = calculate_position_weights(values)

        total_cost = calculate_total_cost_basis(values)

        total_value = calculate_portfolio_value(values)

        total_gain = calculate_portfolio_gain_loss(values)

        total_return = calculate_portfolio_return(values)

        tickers = list(portfolio.positions.keys())
        
        historical_prices = (get_multiple_closing_prices(tickers,period="1y"))

        stock_returns = calculate_daily_returns(historical_prices)

        weights = {
            ticker: data["weight"] / 100
            for ticker, data in values.items()
        }

        portfolio_returns = calculate_portfolio_returns(stock_returns,weights)      

        performance = analyze_portfolio_returns(portfolio_returns)

        #Optimization 
        optimization = optimize_portfolio(stock_returns)
        

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

        all_tickers = tickers + ["SPY"]
        
        all_prices = get_multiple_closing_prices(all_tickers,period="1y")

        benchmark_prices = all_prices["SPY"]

        historical_prices = all_prices.drop(columns=["SPY"])

        benchmark_metrics = analyze_performance(benchmark_prices)

        comparison = compare_performance(performance,benchmark_metrics)

        #Creates portfolio line chart
        portfolio_growth = (1 + portfolio_returns).cumprod()
        
        st.subheader("Portfolio Growth")

        st.line_chart(portfolio_growth)

        #Compares against S&P 500
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

        holdings_df = pd.DataFrame(holdings_data)

        st.subheader("Portfolio Holdings")

        st.dataframe(
            holdings_df,
            use_container_width=True
        )

        
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

        #Cumulative returns
        stock_cumulative_returns = (calculate_stock_cumulative_returns(historical_prices))

        attribution = build_attribution_table(values, stock_cumulative_returns)

        st.subheader(
            "Portfolio Optimization"
        )

        st.write(
            "### Minimum-Volatility Allocation"
        )

        min_vol_df = pd.DataFrame({
            "Ticker": (
                optimization[
                    "minimum_volatility"
                ].keys()
            ),

            "Weight": [
                weight * 100
                for weight
                in optimization[
                    "minimum_volatility"
                ].values()
            ]
        })

        st.dataframe(
            min_vol_df,
            use_container_width=True
        )

        st.write(
            "### Maximum-Sharpe Allocation"
        )

        max_sharpe_df = pd.DataFrame({
            "Ticker": (
                optimization[
                    "maximum_sharpe"
                ].keys()
            ),

            "Weight": [
                weight * 100
                for weight
                in optimization[
                    "maximum_sharpe"
                ].values()
            ]
        })

        st.dataframe(max_sharpe_df, use_container_width=True)

        min_vol_chart = (min_vol_df.set_index("Ticker")["Weight"])

        st.bar_chart(min_vol_chart)

        max_sharpe_chart = (max_sharpe_df.set_index("Ticker")["Weight"])

        st.bar_chart(max_sharpe_chart)

        attribution_df = pd.DataFrame(attribution)

        st.subheader("Performance Attribution")

        display_df = attribution_df.copy()

        display_df["Weight"] = (
            display_df["Weight"]
            .map(lambda x: f"{x:.2f}%")
        )

        display_df["Stock Return"] = (
            display_df["Stock Return"]
            .map(lambda x: f"{x:.2%}")
        )

        display_df["Contribution"] = (
            display_df["Contribution"]
            .map(lambda x: f"{x:.2%}")
        )

        st.dataframe(
            display_df,
            use_container_width=True
        )

        #Contributions chart
        chart_data = (attribution_df.set_index("Ticker")["Contribution"])

        st.bar_chart(chart_data)

        #Monte Carlo Simulation
        expected_return, volatility = (estimate_portfolio_parameters(portfolio_returns))
        initial_value = total_value

        simulation_results = run_monte_carlo(
            expected_return=expected_return,
            volatility=volatility,
            simulations=1000,
            days=252,
            initial_value=initial_value
        )

        simulation_summary = summarize_simulation(simulation_results)

        probability_of_loss = (calculate_probability_of_loss(simulation_results, initial_value))


        simulated_var = calculate_simulated_var(simulation_results,initial_value)


        #Monte Carlo parameters
        simulation_count = st.slider(
            "Number of Simulations",
            min_value=100,
            max_value=10000,
            value=1000,
            step=100
        )

        simulation_years = st.slider(
            "Simulation Horizon (Years)",
            min_value=1,
            max_value=10,
            value=1
        )

        simulation_days = (simulation_years * 252)

        simulation_results = run_monte_carlo(
            expected_return=expected_return,
            volatility=volatility,
            simulations=simulation_count,
            days=simulation_days,
            initial_value=initial_value
        )
        
        with st.expander("Stock-Level Analysis", expanded=True):
            #Analysis of a chosen stock in portfolio
            st.subheader("Stock-Level Analysis")
    
            selected_ticker = st.selectbox(
                "Select a holding",
                options=list(portfolio.positions.keys()),
                key = "selected_stock"
            )
    
            selected_prices = historical_prices[selected_ticker]
    
            stock_metrics = analyze_performance(selected_prices)

            #Cache calls to network
            @st.cache_data(ttl=300)
            def load_prices(tickers, period):
                return get_multiple_closing_prices(tickers,period=period)

            @st.cache_data(ttl=300)
            def load_news(ticker):
                return get_normalized_stock_news(ticker)

            all_prices = load_prices(tickers + ["SPY"], "1y")

            articles = load_news(selected_ticker)
    
            s1, s2, s3, s4 = st.columns(4)
    
            s1.metric(
                "Current Price",
                f"${values[selected_ticker]['current_price']:.2f}"
            )
    
            s2.metric(
                "1Y Return",
                f"{stock_metrics['cumulative_return']:.2%}"
            )
    
            s3.metric(
                "Volatility",
                f"{stock_metrics['annualized_volatility']:.2%}"
            )
    
            s4.metric(
                "Max Drawdown",
                f"{stock_metrics['max_drawdown']:.2%}"
            )
    
            st.metric(
                "Sharpe Ratio",
                f"{stock_metrics['sharpe_ratio']:.2f}"
            )
    
            #Charts of the historical price
            st.subheader(
                f"{selected_ticker} Price History"
            )
    
            st.line_chart(selected_prices)
    
            #Normalize series
            normalized_prices = (selected_prices / selected_prices.iloc[0])
    
            st.subheader(
                f"{selected_ticker} Growth of $1"
            )
    
            st.line_chart(normalized_prices)
    
            stock_drawdown = calculate_drawdown(selected_prices)
    
            st.subheader(
                f"{selected_ticker} Drawdown"
            )
    
            st.line_chart(
                stock_drawdown
            )
    
            position = values[selected_ticker]

            articles = get_normalized_stock_news(selected_ticker)

            analyzed_articles = analyze_news_sentiment(articles[:10])

            sentiment_summary = summarize_sentiment(analyzed_articles)

            st.write("### News Sentiment")

            n1, n2 = st.columns(2)

            n1.metric(
                "Overall Sentiment",
                sentiment_summary[
                    "overall_sentiment"
                ]
            )

            n2.metric(
                "Average Score",
                f"{sentiment_summary['average_score']:.2f}"
            )

            st.write(
            f"### Recent {selected_ticker} News"
            )

            if not analyzed_articles:
                st.info("No recent news found.")

            for article in analyzed_articles:
                st.write(f"**{article['title']}**")

                st.write(
                    f"{article['publisher']} — "
                    f"{article['sentiment_label']} "
                    f"({article['sentiment_score']:.2f})"
                )

                if article["summary"]:
                    st.write(article["summary"])

                if article["url"]:
                    st.link_button(
                        "Read Article",
                        article["url"]
                    )

                st.divider()
    
            st.write("### Position Details")
    
            p1, p2, p3, p4 = st.columns(4)
    
            p1.metric(
                "Shares",
                f"{position['shares']}"
            )
    
            p2.metric(
                "Purchase Price",
                f"${position['purchase_price']:.2f}"
            )
    
            p3.metric(
                "Position Value",
                f"${position['current_value']:,.2f}"
            )
    
            p4.metric(
                "Portfolio Weight",
                f"{position['weight']:.2f}%"
            )
    
            p5, p6 = st.columns(2)
    
            p5.metric(
                "Gain / Loss",
                f"${position['gain_loss']:,.2f}"
            )
    
            p6.metric(
                "Return Since Purchase",
                f"{position['return_percentage']:.2f}%"
            )
    
            selected_returns = calculate_daily_returns(
                selected_prices
            )
    
            st.subheader(
                f"{selected_ticker} Daily Returns"
            )
    
            st.line_chart(selected_returns)

            #Display Monte Carlo stuff
            st.subheader("Monte Carlo Simulation")

            m1, m2, m3, m4 = st.columns(4)

            m1.metric(
                "Current Value",
                f"${initial_value:,.2f}"
            )

            m2.metric(
                "Median Simulated Value",
                f"${simulation_summary['median']:,.2f}"
            )

            m3.metric(
                "Probability of Loss",
                f"{probability_of_loss:.2%}"
            )

            m4.metric(
                "95% VaR",
                f"${simulated_var:,.2f}"
            )

            m5, m6 = st.columns(2)

            m5.metric(
                "5th Percentile",
                f"${simulation_summary['percentile_5']:,.2f}"
            )

            m6.metric(
                "95th Percentile",
                f"${simulation_summary['percentile_95']:,.2f}"
            )

            st.write(
                "### Sample Future Portfolio Paths"
            )

            st.line_chart(
                simulation_results.iloc[:, :50]
            )

            ending_values = (
                simulation_results.iloc[-1]
            )

            st.write(
                "### Distribution of Ending Values"
            )

            st.bar_chart(
                ending_values.value_counts(
                    bins=30
                ).sort_index()
            )


    except ValueError as error:
        st.error(str(error))

    except TypeError as error:
        st.error(
            f"Invalid input: {error}"
        )

    except Exception as error:
        st.error(
            "An unexpected error occurred."
        )

    except Exception as error:
        st.error(
            f"Unable to analyze portfolio: {error}"
        )

    




