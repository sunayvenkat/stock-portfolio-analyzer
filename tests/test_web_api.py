
import json

import numpy as np
import pandas as pd
import pytest
from yfinance.exceptions import YFRateLimitError

from web import api
from web.server import to_json_safe


#Synthetic year of closes, different for each ticker, so the test never touches the network
def fake_closes(ticker, period="1y"):
    rng = np.random.default_rng(sum(map(ord, ticker)))
    dates = pd.date_range("2025-01-01", periods=252, freq="B", tz="America/New_York")

    return pd.Series(100 * np.cumprod(1 + rng.normal(0.0005, 0.01, len(dates))), index=dates)


@pytest.fixture
def offline(monkeypatch):
    calls = []

    def fetch(ticker, period="1y"):
        calls.append(ticker)
        return fake_closes(ticker, period)

    monkeypatch.setattr(api, "get_closing_prices", fetch)
    monkeypatch.setattr(api.time, "sleep", lambda seconds: None)
    api._cache.clear()

    return calls


HOLDINGS = {"holdings": [
    {"ticker": "aapl", "shares": 10, "purchase_price": 150},
    {"ticker": "MSFT", "shares": 5, "purchase_price": 300},
]}


def test_analyze_totals_add_up(offline):
    result = api.analyze(HOLDINGS)

    expected_value = 10 * fake_closes("AAPL").iloc[-1] + 5 * fake_closes("MSFT").iloc[-1]

    assert result["summary"]["current_value"] == pytest.approx(expected_value)
    assert result["summary"]["cost_basis"] == 3000
    assert sum(h["weight"] for h in result["holdings"].values()) == pytest.approx(100)
    assert result["growth"]["portfolio"][0] == 1.0
    assert len(result["growth"]["dates"]) == len(result["growth"]["benchmark"])
    assert sum(result["optimization"]["maximum_sharpe"]["weights"].values()) == pytest.approx(1)
    assert sum(result["simulation"]["histogram"]["counts"]) == 1000

    #The whole response must survive strict JSON encoding
    json.dumps(to_json_safe(result), allow_nan=False)


def test_prices_are_cached_per_ticker(offline):
    api.analyze(HOLDINGS)
    api.analyze({"holdings": [{"ticker": "AAPL", "shares": 1, "purchase_price": 100}]})

    assert sorted(offline) == ["AAPL", "MSFT", "SPY"]


def test_rate_limit_is_retried(offline, monkeypatch):
    attempts = []

    def flaky(ticker, period="1y"):
        attempts.append(ticker)

        if len(attempts) == 1:
            raise YFRateLimitError()

        return fake_closes(ticker, period)

    monkeypatch.setattr(api, "get_closing_prices", flaky)

    api.analyze({"holdings": [{"ticker": "AAPL", "shares": 1, "purchase_price": 100}]})

    assert attempts[:2] == ["AAPL", "AAPL"]


def test_rate_limit_gives_up_after_retries(offline, monkeypatch):
    def limited(ticker, period="1y"):
        raise YFRateLimitError()

    monkeypatch.setattr(api, "get_closing_prices", limited)

    with pytest.raises(YFRateLimitError):
        api.analyze(HOLDINGS)


def test_single_holding_skips_diversification(offline):
    result = api.analyze({"holdings": [{"ticker": "AAPL", "shares": 1, "purchase_price": 100}]})

    assert result["diversification"] is None
    assert result["optimization"] is None


@pytest.mark.parametrize("holding", [
    {"ticker": "AAPL; DROP", "shares": 1, "purchase_price": 1},
    {"ticker": "AAPL", "shares": True, "purchase_price": 1},
    {"ticker": "AAPL", "shares": -1, "purchase_price": 1},
])
def test_analyze_rejects_bad_input(offline, holding):
    with pytest.raises((ValueError, TypeError)):
        api.analyze({"holdings": [holding]})


SIMULATION = {"expected_return": 0.1, "volatility": 0.2, "initial_value": 1000}


@pytest.mark.parametrize("simulations, years", [(10000, 1), (1000, 10), (2500, 4)])
def test_simulate_accepts_runs_inside_the_budget(simulations, years):
    result = api.simulate({**SIMULATION, "simulations": simulations, "years": years})

    assert sum(result["histogram"]["counts"]) == simulations


@pytest.mark.parametrize("simulations, years", [(50000, 1), (10000, 2), (1100, 10)])
def test_simulate_rejects_runs_over_the_budget(simulations, years):
    with pytest.raises(ValueError):
        api.simulate({**SIMULATION, "simulations": simulations, "years": years})


def test_to_json_safe_replaces_nan():
    assert to_json_safe({"a": np.float64("nan"), "b": [np.int64(3)]}) == {"a": None, "b": [3]}


def test_normalize_news_reads_feed_and_search_items():
    from data.news_data import normalize_news

    feed = {"content": {"title": "A", "summary": "s", "provider": {"displayName": "P"}, "canonicalUrl": {"url": "u"}}}
    search = {"title": "B", "publisher": "Q", "link": "l"}

    assert normalize_news([feed, search]) == [
        {"title": "A", "summary": "s", "publisher": "P", "url": "u"},
        {"title": "B", "summary": "", "publisher": "Q", "url": "l"},
    ]
