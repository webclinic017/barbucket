import pytest
from logging import getLogger

from barbucket.domain_model.types import *


_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing Types")


def test_api_correct() -> None:
    _logger.debug(f"---------- Test: test_api_correct")
    try:
        test_api = Api.IB
    except AttributeError as e:
        assert False, e


def test_api_incorrect() -> None:
    _logger.debug(f"---------- Test: test_api_incorrect")
    with pytest.raises(AttributeError):
        test_api = Api.NON_EXIST  # type: ignore


def test_exchange_correct() -> None:
    _logger.debug(f"---------- Test: test_exchange_correct")
    try:
        test_exchange = Exchange.XETRA
    except AttributeError as e:
        assert False, e


def test_exchange_incorrect() -> None:
    _logger.debug(f"---------- Test: test_exchange_incorrect")
    with pytest.raises(AttributeError):
        test_exchange = Exchange.NON_EXIST  # type: ignore


def test_stock_type_correct() -> None:
    _logger.debug(f"---------- Test: test_stock_type_correct")
    try:
        test_contract_type = StockType.ETF
    except AttributeError as e:
        assert False, e


def test_stock_type_incorrect() -> None:
    _logger.debug(f"---------- Test: test_stock_type_incorrect")
    with pytest.raises(AttributeError):
        test_contract_type = StockType.NON_EXIST  # type: ignore


def test_get_api_notation_for_exchange() -> None:
    _logger.debug(f"---------- Test: test_get_api_notation_for_exchange")
    trans = ApiNotationTranslator()
    expected = "IBIS"
    actual = trans.get_api_notation_for_exchange(
        exchange=Exchange.XETRA,
        api=Api.IB)
    assert actual == expected


def test_get_exchange_from_api_notation() -> None:
    _logger.debug(f"---------- Test: test_get_exchange_from_api_notation")
    trans = ApiNotationTranslator()
    expected = Exchange.XETRA
    actual = trans.get_exchange_from_api_notation(
        name="IBIS",
        api=Api.IB)
    assert actual == expected


def test_get_api_notation_for_contract_type() -> None:
    _logger.debug(f"---------- Test: test_get_api_notation_for_contract_type")
    trans = ApiNotationTranslator()
    expected = "COMMON"
    actual = trans.get_api_notation_for_stock_type(
        stock_type=StockType.COMMON_STOCK,
        api=Api.IB)
    assert actual == expected


def test_get_contract_type_from_api_notation() -> None:
    _logger.debug(f"---------- Test: test_get_contract_type_from_api_notation")
    trans = ApiNotationTranslator()
    expected = StockType.COMMON_STOCK
    actual = trans.get_stock_type_from_api_notation(
        name="COMMON",
        api=Api.IB)
    assert actual == expected


def test_get_api_notation_for_ticker_symbol() -> None:
    _logger.debug(f"---------- Test: test_get_api_notation_for_ticker_symbol")
    trans = ApiNotationTranslator()
    expected = "AB CD"
    actual = trans.get_api_notation_for_ticker_symbol(
        ticker_symbol=TickerSymbol(name="AB_CD"),
        api=Api.IB)
    assert actual == expected


def test_get_ticker_symbol_from_api_notation() -> None:
    _logger.debug(f"---------- Test: test_get_ticker_symbol_from_api_notation")
    trans = ApiNotationTranslator()
    ticker_symbol = trans.get_ticker_symbol_from_api_notation(
        name="AB CD",
        api=Api.IB)
    assert type(ticker_symbol) == TickerSymbol
    assert ticker_symbol.name == "AB_CD"
