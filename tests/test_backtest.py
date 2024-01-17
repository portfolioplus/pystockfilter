from datetime import datetime
from unittest.mock import patch

import pytest
from pony.orm import db_session

import pystockfilter.tool.start_backtest as start_backtest
import pystockfilter.tool.start_optimizer as start_optimizer
import pystockfilter.tool.start_seq_optimizer as start_seq_optimizer
from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy as ema
from pystockfilter.strategy.rsi_strategy import RSIStrategy as rsi
from pystockfilter.strategy.uo_ema_cross_close_strategy import (
    UltimateEmaCrossCloseStrategy as uo2,
)
from pystockfilter.strategy.uo_ema_cross_ema_strategy import (
    UltimateEmaCrossEmaStrategy as uo1,
)


@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_backtesting(mock_datetime_now, setup_test_database):
    strategies = [rsi, uo1, uo2]
    parameters = [
        {
            "para_rsi_window": 14,
            "para_rsi_enter": 30,
            "para_rsi_exit": 70,
        },
        {
            "para_ema_short": 7,
            "para_uo_short": 7,
            "para_uo_medium": 14,
            "para_uo_long": 28,
            "para_ema_short": 12,
            "para_uo_upper": 20,
            "para_uo_lower": 0,
        },
        {
            "para_ema_short": 7,
            "para_ema_long": 20,
            "para_uo_short": 7,
            "para_uo_medium": 14,
            "para_uo_long": 28,
            "para_ema_short": 12,
            "para_uo_upper": 20,
            "para_uo_lower": 0,
        },
    ]
    stocks = ["IFX.F"]
    bt = start_backtest.StartBacktest(
        stocks, strategies, parameters, data_source=Data(source=Data.PY_STOCK_DB)
    )
    stats = bt.run()
    assert len(stats) == 3
    assert pytest.approx(stats[0].earnings, 0.01) == 31.55
    assert pytest.approx(stats[1].earnings, 0.01) == 0.0
    assert pytest.approx(stats[2].earnings, 0.01) == 0.0


@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_optimizer(mock_datetime_now, setup_test_database):
    strategies = [ema]
    stocks = ["IFX.F"]
    parameters = [
        ema.get_optimizer_parameters(),
    ]
    bt = start_optimizer.StartOptimizer(
        stocks, strategies, parameters, data_source=Data(source=Data.PY_STOCK_DB)
    )
    stats = bt.run()
    assert len(stats) == 1
    assert pytest.approx(stats[0].earnings, 0.01) == 64.82


@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@db_session
def test_seq_optimizer(mock_datetime_now, setup_test_database):
    strategies = [rsi]
    stocks = ["IFX.F"]
    parameters = [
        [
            {
                "para_rsi_window": range(14, 100, 1),
                "maximize": "Equity Final [$]",
            },
            {
                "para_rsi_enter": range(50, 100, 1),
                "para_rsi_exit": range(20, 60, 1),
                "constraint": lambda p: p.para_rsi_enter > p.para_rsi_exit
                and p.para_rsi_enter - p.para_rsi_exit > 10,
                "maximize": "Equity Final [$]",
            },
        ]
    ]
    bt = start_seq_optimizer.StartSequentialOptimizer(
        stocks, strategies, parameters, data_source=Data(source=Data.PY_STOCK_DB)
    )
    stats = bt.run()
    assert len(stats) == 1
    assert pytest.approx(stats[0].earnings, 0.01) == 14.32
    assert stats[0].parameter["para_rsi_window"] == 14
    assert stats[0].parameter["para_rsi_enter"] == 50
    assert stats[0].parameter["para_rsi_exit"] == 24
