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


class StartSequentialOptimizer(StartBase):
    """A sequential optimizer for strategy parameters. Optimizes the first set of parameters,
    uses the optimized parameters to refine the next set, and continues this process to
    reduce overall optimization time and improve strategy performance iteratively."""

    def __init__(
        self,
        ticker_symbols: list[str],
        strategies: list[BaseStrategy],
        optimizer_parameters: list[list[dict]],
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
        parameters: list[dict],
    ) -> BacktestResult:
        if df.empty:
            return None
        previous_result: BacktestResult = None
        best_parameters: dict = {}
        start_time = datetime.now()
        for parameter in parameters:
            if len(best_parameters) > 0:
                # Use parameters from the previous optimization result
                strategy.set_parameters(strategy, best_parameters)
            # Initialize and run backtest
            bt = Backtest(
                df,
                strategy,
                commission=commission,
                cash=cash,
                trade_on_close=True,
                exclusive_orders=True,
            )
            res = bt.optimize(**parameter)
            previous_result = BacktestResult.from_stats_pd(symbol, res, bt)
            best_parameters.update(previous_result.parameter)
        previous_result.parameter = best_parameters
        previous_result.time_taken = (datetime.now() - start_time).total_seconds()
        return previous_result
