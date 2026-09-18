# stock-portfolio-analyzer
Link: https://stock-portfolio-analyzer-spk.streamlit.app/

Stock Portfolio Analyzer is an interactive Python application for evaluating investment portfolios using real-time and historical market data. Built with Streamlit, the platform combines portfolio valuation, performance analysis, risk metrics, diversification analysis, benchmark comparison, optimization, Monte Carlo simulation, and financial news sentiment into a single dashboard.

Users can enter multiple stock holdings and instantly analyze portfolio value, gain/loss, asset weights, historical returns, volatility, Sharpe ratio, maximum drawdown, and correlation. The application also compares performance against the S&P 500, identifies individual stock contributions to portfolio returns, and generates minimum-volatility and maximum-Sharpe allocations using quantitative optimization techniques.

For deeper risk analysis, the project includes Monte Carlo simulations that model thousands of potential future portfolio outcomes and estimate metrics such as probability of loss and simulated Value at Risk. Stock-level pages provide detailed historical performance, drawdown analysis, and recent financial news with sentiment scoring.

The project was designed with a modular architecture separating data collection, portfolio models, analytics, and the user interface. Automated testing with pytest helps validate the financial calculations and maintain reliability as new features are added.

Key Features
    Multi-stock portfolio input and live valuation
    Cost basis, gain/loss, and portfolio weight analysis
    Historical return and performance analytics
    Annualized volatility, Sharpe ratio, and maximum drawdown
    S&P 500 benchmark comparison
    Diversification, concentration, and correlation analysis
    Stock-level performance dashboards
    Performance attribution by holding
    Minimum-volatility and maximum-Sharpe portfolio optimization
    Monte Carlo portfolio simulations
    Probability-of-loss and Value-at-Risk analysis
    Financial news retrieval and sentiment analysis
    Interactive Streamlit dashboard
    Automated unit testing with pytest
