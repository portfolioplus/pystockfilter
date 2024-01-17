# test_pystockfilter.py

import pytest
from pystockfilter.tool.build_internal_filters import BuildInternalFilters
from pystockfilter.tool.build_filters import BuildFilters
from pystockfilter.filter.rsi_filter import RsiFilter
from pystockfilter.filter.adx_filter import AdxFilter
from pystockfilter.filter.stock_is_hot_secure import StockIsHotSecure
from pystockfilter.filter.stock_is_hot import StockIsHot
from pystockfilter.base.base_helper import BaseHelper
import logging

from datetime import datetime

from pony.orm import db_session
from pystockdb.db.schema.stocks import Signal, Stock, Tag, db
import sys

from pystockfilter.filter.base_filter import BaseFilter
from tests.helper import get_bars, get_index_bars

sys.path.insert(0, "src")


@db_session
def test_internal_create(setup_test_database):
    logger = BaseHelper.setup_logger("test")
    cfg = {
        "symbols": ["ADS.F"],
        "now_date": datetime.strptime("2019-08-07", "%Y-%m-%d"),
    }
    builder = BuildInternalFilters(cfg, logger)
    assert builder.build() == 0
    signal = Signal.select(lambda s: "AdxP14" in s.item.tags.name).first()
    assert signal is not None
    assert 23.40 == pytest.approx(signal.result.value, abs=0.01)
    cfg["symbols"] = ["ALL"]
    builder = BuildInternalFilters(cfg, logger)
    builder.build()


@db_session
def test_build():
    logger = BaseHelper.setup_logger("test")
    my_filter = StockIsHot(
        {
            "name": "StockIsHot6Month",
            "bars": True,
            "index_bars": False,
            "args": {
                "threshold_buy": 0.8,
                "threshold_sell": 0.5,
                "intervals": [7, 30],
                "lookback": 6,
            },
        },
        logger,
    )
    builder = BuildFilters({}, logger)
    assert builder.build() == 1
    builder = BuildFilters(
        {
            "filters": [my_filter],
            "symbols": ["IFX.F"],
            "now_date": datetime(2019, 10, 5, 18, 00),
        },
        logger,
    )
    assert builder.build() == 0
    with db_session:
        tag_ctx = Tag.select(lambda t: t.name == "StockIsHot6Month").count()
        assert tag_ctx == 1


@db_session
def test_stock_is_hot():
    args = {
        "name": "StockIsHot",
        "bars": True,
        "index_bars": False,
        "args": {
            "threshold_buy": 0.8,
            "threshold_sell": 0.5,
            "intervals": [7, 30],
            "lookback": 6,
        },
    }
    __filter_test(StockIsHot, args, [BaseFilter.HOLD, 0.5625])


@db_session
def test_stock_is_hot_secure():
    args = {
        "name": "StockIsHotSec",
        "bars": True,
        "index_bars": False,
        "args": {
            "threshold_buy": 0.8,
            "threshold_sell": 0.5,
            "intervals": [7, 30],
            "lookback": 6,
            "secure_value": 7,
        },
    }
    __filter_test(StockIsHotSecure, args, [BaseFilter.SELL, 0.38])


@db_session
def test_adx():
    args = {
        "name": "adx",
        "bars": True,
        "index_bars": False,
        "args": {
            "threshold_buy": 0.8,
            "threshold_sell": 0.5,
            "intervals": [7, 30],
            "lookback": 6,
            "parameter": 5,
        },
    }
    __filter_test(AdxFilter, args, [BaseFilter.BUY, 42.41])


@db_session
def test_rsi():
    args = {
        "name": "rsi",
        "bars": True,
        "index_bars": False,
        "args": {
            "threshold_buy": 0.8,
            "threshold_sell": 0.5,
            "intervals": [7, 30],
            "lookback": 6,
            "parameter": 5,
        },
    }
    __filter_test(RsiFilter, args, [BaseFilter.BUY, 51.71])


def __filter_test(filter_class, args, result):
    logger = logging.getLogger("test")
    fil = filter_class(args, logger)
    if fil.lookback and fil.need_bars:
        fil.set_bars(get_bars("IFX.F", fil))
    if fil.lookback and fil.need_index_bars:
        fil.set_index_bars(get_index_bars("IFX.F", fil))
    stock = Stock.select((lambda s: "IFX.F" in s.price_item.symbols.name)).first()
    fil.set_stock(stock)
    strategy_status = fil.analyse()
    strategy_value = fil.get_calculation()
    assert strategy_status == result[0]
    assert strategy_value == pytest.approx(result[1], abs=0.01)
