# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from typing import Type
import pandas as pd
from pystockfilter.data import StockDataSource
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.chunked_optimizer import ChunkedOptimizer
from pystockfilter.tool.result import BacktestResult
from pystockfilter.tool.start_base import StartBase


class StartChunkedOptimizer(StartBase):

    def __init__(
        self,
        ticker_symbols: list[str],
        strategies: list[BaseStrategy],
        optimizer_parameters: list[dict],
        optimizer_class: Type[StartBase],
        data_source: StockDataSource,
        data_chunk_size=100,
    ):

        super().__init__(ticker_symbols, strategies, optimizer_parameters, data_source)
        self.data_chunk_size = data_chunk_size
        self.optimizer_class = optimizer_class
        self.optimizer_parameters = optimizer_parameters

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
        bt = ChunkedOptimizer(
            strategy,
            symbol,
            parameter,
            df,
            commission=commission,
            cash=cash,
            data_chunk_size=self.data_chunk_size,
            optimizer_class=self.optimizer_class,
        )
        result = bt.optimize()
        return result

    def validate(self):
        if not issubclass(self.optimizer_class, StartBase):
            raise ValueError("Optimizer class must be a subclass of StartBase")

        # data chunk size must be greater than parameter of optimizer
        for param_dict in self.optimizer_parameters:
            for key, value in param_dict.items():
                if key.startswith("para_") and not any(
                    sub in key for sub in ["enter", "exit"]
                ):
                    if value > self.data_chunk_size:
                        raise ValueError(
                            f"{key} must be lower than data chunk size ({self.data_chunk_size})."
                        )
