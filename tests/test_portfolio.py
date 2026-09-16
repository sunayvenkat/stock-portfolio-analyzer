import pytest
from models.portfolio import Portfolio


def test_create_portfolio():
    portfolio = Portfolio("Test Portfolio")

    assert portfolio.name == "Test Portfolio"
    assert portfolio.positions == {}


def test_add_position():
    portfolio = Portfolio("Test Portfolio")

    portfolio.add_position("AAPL", 10, 230)

    position = portfolio.get_position("AAPL")

    assert position["shares"] == 10
    assert position["purchase_price"] == 230


def test_ticker_formatting():
    portfolio = Portfolio("Test Portfolio")

    portfolio.add_position(" aapl ", 10, 230)

    assert portfolio.get_position("AAPL") is not None


def test_remove_position():
    portfolio = Portfolio("Test Portfolio")

    portfolio.add_position("AAPL", 10, 230)
    portfolio.remove_position("AAPL")

    assert portfolio.get_position("AAPL") is None


def test_total_cost():
    portfolio = Portfolio("Test Portfolio")

    portfolio.add_position("AAPL", 10, 230)
    portfolio.add_position("NVDA", 5, 180)

    assert portfolio.total_cost() == 3200


def test_negative_shares():
    portfolio = Portfolio("Test Portfolio")

    with pytest.raises(ValueError):
        portfolio.add_position("AAPL", -10, 230)


def test_negative_price():
    portfolio = Portfolio("Test Portfolio")

    with pytest.raises(ValueError):
        portfolio.add_position("AAPL", 10, -230)


def test_empty_ticker():
    portfolio = Portfolio("Test Portfolio")

    with pytest.raises(ValueError):
        portfolio.add_position("", 10, 230)


def test_invalid_shares_type():
    portfolio = Portfolio("Test Portfolio")

    with pytest.raises(TypeError):
        portfolio.add_position("AAPL", "ten", 230)


def test_invalid_price_type():
    portfolio = Portfolio("Test Portfolio")

    with pytest.raises(TypeError):
        portfolio.add_position("AAPL", 10, "230")

def test_invalid_ticker_type():
    portfolio = Portfolio("Test Portfolio")

    with pytest.raises(TypeError):
        portfolio.add_position(123, 10, 230)