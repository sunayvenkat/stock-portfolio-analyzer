# stock-portfolio-analyzer
Link: https://stock-portfolio-analyzer-spk.streamlit.app/

Stock Portfolio Analyzer is an interactive Python application for evaluating investment portfolios using real-time and historical market data. Built with Streamlit, the platform combines portfolio valuation, performance analysis, risk metrics, diversification analysis, benchmark comparison, optimization, Monte Carlo simulation, and financial news sentiment into a single dashboard.

Users can enter multiple stock holdings and instantly analyze portfolio value, gain/loss, asset weights, historical returns, volatility, Sharpe ratio, maximum drawdown, and correlation. The application also compares performance against the S&P 500, identifies individual stock contributions to portfolio returns, and generates minimum-volatility and maximum-Sharpe allocations using quantitative optimization techniques.

For deeper risk analysis, the project includes Monte Carlo simulations that model thousands of potential future portfolio outcomes and estimate metrics such as probability of loss and simulated Value at Risk. Stock-level pages provide detailed historical performance, drawdown analysis, and recent financial news with sentiment scoring.

The project was designed with a modular architecture separating data collection, portfolio models, analytics, and the user interface. Automated testing with pytest helps validate the financial calculations and maintain reliability as new features are added.

Web App (no Streamlit)
    web/ holds a standalone version of the dashboard: a small server built on the Python standard library (web/server.py) that runs the same analytics, and a plain HTML, CSS and JavaScript front end (web/static/) with no framework or CDN dependencies.

    Run it from the project root:
        python web/server.py
    then open http://127.0.0.1:8000.

    To host it so it stays up, run the same command on any machine or service that runs Python (a VPS, Render, Railway, Fly.io, a home server) with HOST=0.0.0.0 and PORT set to the port the host expects. It still needs internet access, because prices and news come from Yahoo Finance.

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
