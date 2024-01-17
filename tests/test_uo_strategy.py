from datetime import datetime
import logging
from pystockfilter.filter.base_filter import BaseFilter
from pystockfilter.strategy.uo_strategy import UlimateStrategy as uo
from pystockfilter.strategy.uo_ema_cross_ema_strategy import (
    UlimateEmaCrossEmaStrategy as uo1,
)
from pystockfilter.strategy.uo_ema_cross_close_strategy import (
    UlimateEmaCrossCloseStrategy as uo2,
)
from pystockfilter.tool.helper import float_range_list
import pystockfilter.tool.start_backtest as start_backtest
from pystockfilter.tool.start_chunked_optimizer import StartChunkedOptimizer
import pystockfilter.tool.start_optimizer as start_optimizer

from tests.helper import get_bars
from pony.orm import db_session
import pytest
from unittest.mock import patch


@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_uo(mock_datetime_now, setup_test_database):
    strategies = [uo]
    stocks = ["IFX.F"]
    bt = start_backtest.StartBacktest(stocks, strategies)
    stats = bt.run_backtest()
    assert len(stats) == 1
    assert pytest.approx(stats[0].stats["Return [%]"], 0.01) == -4.86


@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_uo_optimize(mock_datetime_now, setup_test_database):
    uo.para_uo_upper = 25
    uo.para_uo_lower = 2
    parameters = [
        {
            "para_uo_short": range(1, 20, 1),
            "para_uo_medium": range(1, 50, 1),
            "para_uo_long": range(1, 100, 1),
            "constraint": lambda p: p.para_uo_long > p.para_uo_medium > p.para_uo_short,
            "maximize": "Equity Final [$]",
            "max_tries": 200,
        }
    ]
    strategies = [uo]
    stocks = ["IFX.F"]
    bt = start_optimizer.StartOptimizer(stocks, strategies, parameters)
    stats = bt.run()
    assert len(stats) == 1


@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_uo_optimize_2(mock_datetime_now, setup_test_database):
    parameters = [
        {
            "para_uo_upper": range(-20, 100, 1),
            "para_uo_lower": range(-80, 50, 1),
            "constraint": lambda p: p.para_uo_upper > p.para_uo_lower,
            "maximize": "Equity Final [$]",
            "max_tries": 2000,
        }
    ]
    strategies = [uo]
    stocks = ["IFX.F"]
    bt = start_optimizer.StartOptimizer(stocks, strategies, parameters)
    stats = bt.run()
    assert len(stats) == 1

def constraint_uo(p):
    return p.para_uo_upper > p.para_uo_lower

@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_uo_chunked_optimize(mock_datetime_now, setup_test_database):
    parameters = [
        {
            "para_uo_upper": range(-20, 100, 1),
            "para_uo_lower": range(-80, 50, 1),
            "constraint": constraint_uo,
            "maximize": "Equity Final [$]",
            "max_tries": 2000,
        }
    ]
    strategies = [uo]
    stocks = ["IFX.F"]
    bt = StartChunkedOptimizer(stocks, strategies, parameters)
    stats = bt.run()
    assert len(stats) == 1
