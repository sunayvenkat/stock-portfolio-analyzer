

from vaderSentiment.vaderSentiment import (
    SentimentIntensityAnalyzer,
)


analyzer = SentimentIntensityAnalyzer()

#Runs sentiment analysis on given test
def analyze_text_sentiment(text):
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    scores = analyzer.polarity_scores(text)

    return scores

#Classifies a given sentiment score
def classify_sentiment(score):
    if score >= 0.05:
        return "Positive"

    if score <= -0.05:
        return "Negative"

    return "Neutral"

#Runs sentiment analysis on an entire article
def analyze_article_sentiment(article):
    text = (
        f"{article.get('title', '')} "
        f"{article.get('summary', '')}"
    ).strip()

    scores = analyze_text_sentiment(text)

    return {
        **article,
        "sentiment_score": scores["compound"],
        "sentiment_label": classify_sentiment(
            scores["compound"]
        ),
    }

#Analyzes multiple articles
def analyze_news_sentiment(articles):
    return [
        analyze_article_sentiment(article)
        for article in articles
    ]

#Calculates an average sentiment score
def calculate_average_sentiment(
    analyzed_articles
):
    if not analyzed_articles:
        return 0.0

    scores = [
        article["sentiment_score"]
        for article in analyzed_articles
    ]

    return sum(scores) / len(scores)

def summarize_sentiment(
    analyzed_articles
):
    average_score = calculate_average_sentiment(
        analyzed_articles
    )

    return {
        "average_score": average_score,
        "overall_sentiment":
            classify_sentiment(
                average_score
            ),
        "article_count":
            len(analyzed_articles),
    }

