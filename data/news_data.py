

import yfinance as yf
from utils.logger import logger

#Returns news on a given stock ticker
def get_stock_news(ticker):
    if not isinstance(ticker, str):
        raise TypeError("Ticker symbol must be a string.")

    ticker = ticker.upper().strip()

    if not ticker:
        raise ValueError("Ticker symbol cannot be empty.")

    logger.info("Fetching news for %s", ticker)

    stock = yf.Ticker(ticker)

    news = stock.news

    if not news:
        logger.warning("No news found for %s",ticker)

        return []

    logger.info("Fetched %d news articles for %s", len(news), ticker)

    return news

#Turns raw dictionary of news titles into manageable stuff
def normalize_news(raw_news):
    articles = []

    for item in raw_news:
        content = item.get("content", {})

        title = content.get("title", "")
        summary = content.get("summary", "")

        provider = content.get(
            "provider",
            {}
        )

        publisher = provider.get(
            "displayName",
            "Unknown"
        )

        canonical_url = content.get(
            "canonicalUrl",
            {}
        )

        url = canonical_url.get(
            "url",
            ""
        )

        articles.append({
            "title": title,
            "summary": summary,
            "publisher": publisher,
            "url": url,
        })

    return articles

#Normalizes news on a ticker
def get_normalized_stock_news(ticker):
    raw_news = get_stock_news(ticker)

    return normalize_news(raw_news)
