import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from pystockfilter.backtesting import Backtest, Strategy
from pystockfilter.tool.start_base import BacktestResult, Signals
from pystockfilter.tool.start_batch_optimizer import StartBatchOptimizer
import numpy as np


class MockStrategy(Strategy):
    # Mock strategy class inheriting from Strategy to pass type check in Backtest
    param = 1  # Define the required parameter as a class variable

    def init(self):
        pass

    def next(self):
        pass

def test_optimizer_initialization():
    # Ensure that the optimizer initializes correctly with provided parameters
    ticker_symbols = ["AAPL", "GOOG"]
    strategies = [MockStrategy]  # Use MockStrategy to satisfy Strategy requirement
    optimizer_parameters = [{"param1": 5}]
    data_source = MagicMock()

    optimizer = StartBatchOptimizer(ticker_symbols, strategies, optimizer_parameters, data_source)

    assert optimizer.ticker_symbols == ticker_symbols
    assert optimizer.strategies == strategies
    assert optimizer.parameters == optimizer_parameters
