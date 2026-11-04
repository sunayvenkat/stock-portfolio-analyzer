

import yfinance as yf
from yfinance.exceptions import YFDataException
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

    #Yahoo's news feed sometimes answers with a maintenance page; its search API carries the same headlines
    try:
        news = stock.news
    except YFDataException:
        logger.warning("News feed unavailable for %s; using Yahoo search instead", ticker)

        news = yf.Search(ticker, news_count=10, max_results=0).news

    if not news:
        logger.warning("No news found for %s",ticker)

        return []

    logger.info("Fetched %d news articles for %s", len(news), ticker)

    return news

#Turns raw dictionary of news titles into manageable stuff
def normalize_news(raw_news):
    articles = []

    for item in raw_news:
        #Feed items nest their fields under "content"; search items are flat
        content = item.get("content", item)

        title = content.get("title", "")
        summary = content.get("summary", "")

        provider = content.get(
            "provider",
            {}
        )

        publisher = provider.get(
            "displayName",
            content.get("publisher", "Unknown")
        )

        canonical_url = content.get(
            "canonicalUrl",
            {}
        )

        url = canonical_url.get(
            "url",
            content.get("link", "")
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
