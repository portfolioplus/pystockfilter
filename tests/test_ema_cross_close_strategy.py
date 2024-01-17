import pandas as pd
import pytest
from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy
from backtesting import Backtest


def test_ema_cross_close_strategy(apple_data):
    bt = Backtest(apple_data, EmaCrossCloseStrategy, cash=10000, commission=0.002)
    stats = bt.run()
    assert stats["_trades"].shape[0] == 3


def test_optimize_ema_cross_close_strategy(apple_data):
    bt = Backtest(apple_data, EmaCrossCloseStrategy, cash=10000, commission=0.002)
    stats = bt.optimize(
        para_ema=range(90, 100, 1),
        maximize="Equity Final [$]",
    )
    para = stats["_strategy"].get_parameters() 
    assert para == {'para_ema': 96}
