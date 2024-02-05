from datetime import datetime
from pystockfilter.strategy.rsi_strategy import RSIStrategy as rsi
from pystockfilter.strategy.uo_ema_cross_ema_strategy import (
    UltimateEmaCrossEmaStrategy as uo1,
)
from pystockfilter.strategy.uo_ema_cross_close_strategy import (
    UltimateEmaCrossCloseStrategy as uo2,
)
from pystockfilter.tool.helper import float_range_list
import pystockfilter.tool.start_backtest as start_backtest
import pystockfilter.tool.start_optimizer as start_optimizer

from tests.helper import get_bars
from pystockdb.db.schema.stocks import Stock
from pony.orm import db_session
import pytest
from unittest.mock import patch
from backtesting.test import SMA


@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_backtesting(mock_datetime_now, setup_test_database):
    strategies = [rsi, uo1, uo2]
    stocks = ["IFX.F"]
    bt = start_backtest.StartBacktest(stocks, strategies)
    stats = bt.run()
    assert len(stats) == 3
    assert pytest.approx(stats[0].stats["Return [%]"], 0.01) == 5.9


@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_optimizer(mock_datetime_now, setup_test_database):
    strategies = [rsi]
    stocks = ["IFX.F"]
    parameters = [
        {
            "para_rsi_window": range(28, 30, 1),
            "para_rsi_enter": range(98, 100, 1),
            "para_rsi_exit": range(48, 50, 1),
            "constraint": lambda p: p.para_rsi_exit < p.para_rsi_enter,
            "maximize": "Equity Final [$]",
        }
    ]
    bt = start_optimizer.StartOptimizer(stocks, strategies, parameters)
    stats = bt.run()
    assert len(stats) == 1
    assert pytest.approx(stats[0].to_dict()["stats"]["return_percent"], 0.01) == 2.24
