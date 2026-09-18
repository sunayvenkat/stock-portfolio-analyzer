

import pytest

from analytics.sentiment import (
    analyze_text_sentiment,
    classify_sentiment,
    calculate_average_sentiment,
)


def test_positive_sentiment():
    result = analyze_text_sentiment(
        "The company reported excellent growth "
        "and record profits."
    )

    assert result["compound"] > 0


def test_negative_sentiment():
    result = analyze_text_sentiment(
        "The company reported severe losses "
        "and disappointing results."
    )

    assert result["compound"] < 0


def test_classify_positive():
    assert classify_sentiment(
        0.50
    ) == "Positive"


def test_classify_negative():
    assert classify_sentiment(
        -0.50
    ) == "Negative"


def test_classify_neutral():
    assert classify_sentiment(
        0.01
    ) == "Neutral"

def test_average_sentiment():
    articles = [
        {"sentiment_score": 0.4},
        {"sentiment_score": 0.2},
    ]

    result = calculate_average_sentiment(
        articles
    )

    assert result == pytest.approx(0.3)

