# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from datetime import datetime
from pystockfilter.backtesting import Backtest

from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.start_base import StartBase
from pystockfilter.tool.result import BacktestResult
from typing import Type

from pystockfilter.tool.start_optimizer import StartOptimizer
from pystockfilter import logger


class ChunkedOptimizer:
    def __init__(
        self,
        strategy: BaseStrategy,
        symbol: str,
        optimizer_arg,
        data,
        data_chunk_size=100,
        commission=0.002,
        cash=10000,
        exclusive_orders=True,
        trade_on_close=True,
        optimizer_class: Type[StartBase] = StartOptimizer,
    ):
        self.data = data
        self.symbol = symbol
        self.data_chunk_size = data_chunk_size
        self.strategy = strategy
        self.optimizer_arg = optimizer_arg
        self.cash = cash
        self.commission = commission
        self.exclusive_orders = exclusive_orders
        self.trade_on_close = trade_on_close
        self.optimizer_class = optimizer_class

    def _chunks(self, data):
        for i in range(0, len(data), self.data_chunk_size):
            chunk = (
                data[i : i + self.data_chunk_size],
                self.strategy,
                self.optimizer_arg,
                self.optimizer_class,
                self.cash,
                self.commission,
                self.exclusive_orders,
                self.trade_on_close,
            )
            yield chunk

    @staticmethod
    def _optimize_strategy(args):
        (
            chunk,
            strategy,
            optimizer_arg,
            optimizer_class,
            cash,
            commission,
            exclusive_orders,
            trade_on_close,
        ) = args

        # Initialize optimizer with None as data source and run optimization
        optimizer: StartBase = optimizer_class(None, None, None, None)
        result = optimizer.run_implementation(
            strategy, "", chunk, commission, cash, optimizer_arg
        )
        return (result.sqn, result.parameter)

    def optimize(self) -> dict:
        start_time = datetime.now()
        all_chunks = list(self._chunks(self.data))
        results = []

        for chunk in all_chunks:
            try:
                sqn, best_params = self._optimize_strategy(chunk)
                results.append(best_params)
                logger.debug(f"Chunked optimization: {best_params} - {sqn}")
            except ValueError as e:
                logger.warning(
                    f"Error in chunked optimization. Data chunk skipped. Error: {e}"
                )

        # The rest of the method remains the same
        best_result = None
        for best_param in results:
            self.strategy.set_parameters(self.strategy, best_param)
            bt = Backtest(
                self.data,
                self.strategy,
                cash=self.cash,
                commission=self.commission,
                exclusive_orders=self.exclusive_orders,
                trade_on_close=self.trade_on_close,
            )

            stats = bt.run()
            result = BacktestResult.from_stats_pd(
                symbol=self.symbol, stats=stats, bt=bt, time_taken=0.0
            )
            result.parameter = best_param
            if best_result is None or result > best_result:
                best_result = result
        if best_result is not None:
            time_taken = (datetime.now() - start_time).total_seconds()
            best_result.time_taken = time_taken
        return best_result
