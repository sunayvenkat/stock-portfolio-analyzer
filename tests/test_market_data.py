import pytest

from data.market_data import (
    get_historical_prices,
    get_closing_prices
)


def test_historical_prices_invalid_ticker_type():
    with pytest.raises(TypeError):
        get_historical_prices(123)


def test_historical_prices_empty_ticker():
    with pytest.raises(ValueError):
        get_historical_prices("")