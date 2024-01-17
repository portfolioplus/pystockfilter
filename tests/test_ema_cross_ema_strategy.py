import json
import multiprocessing as mp
import pandas as pd
import pytest
from pystockfilter.strategy.ema_cross_ema_strategy import EmaCrossEmaStrategy
from backtesting import Backtest

from pystockfilter.tool.chunked_optimizer import ChunkedOptimizer


def test_ema_cross_ema_strategy(apple_data):
    EmaCrossEmaStrategy.para_ema_short = 7
    EmaCrossEmaStrategy.para_ema_long = 121
    bt = Backtest(
        apple_data,
        EmaCrossEmaStrategy,
        cash=10000,
        commission=0.002,
        exclusive_orders=True,
        trade_on_close=True,
    )
    stats = bt.run()
    assert stats["_trades"].shape[0] == 170

def constraint(p):
    return p.para_ema_long > p.para_ema_short

def test_optimize_ema_cross_ema_strategy(apple_data):

    opti = ChunkedOptimizer(
        EmaCrossEmaStrategy,
        {
            "para_ema_short": range(48, 50, 1),
            "para_ema_long": range(148, 150, 1),
            "constraint": constraint,
            "maximize": "Equity Final [$]",
        },
        data= apple_data,
        chunk_size=365,
        num_processes=mp.cpu_count() - 1,
        cash=10000,
        commission=0.002,
        exclusive_orders=True,
        trade_on_close=True,
    )
    result = opti.optimize()
    # todo put strategy object in result
    parameters = result["_strategy"].get_parameters()
    assert {"para_ema_long": 148, "para_ema_short": 48} == parameters
