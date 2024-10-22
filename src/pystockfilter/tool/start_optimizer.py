# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from datetime import datetime
from pystockfilter.backtesting import Backtest
import pandas as pd
from pystockfilter.data import StockDataSource
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.result import BacktestResult
from pystockfilter.tool.start_base import StartBase


class StartOptimizer(StartBase):

    def __init__(
        self,
        ticker_symbols: list[str],
        strategies: list[BaseStrategy],
        optimizer_parameters: list[dict],
        data_source: StockDataSource,
    ):

        super().__init__(ticker_symbols, strategies, optimizer_parameters, data_source)

    def run_implementation(
        self,
        strategy: BaseStrategy,
        symbol: str,
        df: pd.DataFrame,
        commission: float,
        cash: float,
        parameter: dict,
    ) -> BacktestResult:
        if df.empty:
            return None
        bt = Backtest(
            df,
            strategy,
            commission=commission,
            cash=cash,
            trade_on_close=True,
            exclusive_orders=True,
        )
        start_time = datetime.now()
        result = bt.optimize(**parameter)
        time_taken = (datetime.now() - start_time).total_seconds()
        return BacktestResult.from_stats_pd(symbol, result, bt, time_taken)
