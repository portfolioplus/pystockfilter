# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from pystockfilter.backtesting import Backtest
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from pystockfilter.data import StockDataSource
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.helper import my_now
from pystockfilter import logger
from pystockfilter.tool.result import BacktestResult, BacktestResultList


class StartBase:
    def __init__(
        self,
        ticker_symbols: list[str],
        strategies: list[BaseStrategy],
        parameters: list[dict],
        data_source: StockDataSource,
    ):
        self.strategies: list[BaseStrategy] = strategies
        self.parameters: list[dict] = parameters
        self.ticker_symbols: list[str] = ticker_symbols
        self.data_source = data_source

    def get_data(self, symbol: str, history_months: int) -> pd.DataFrame:
        now = my_now()
        before = now + relativedelta(months=-history_months)
        df = self.data_source.get_stock_data(symbol, before, now)
        return df

    def run(
        self, commission=0.002, cash=10000.0, history_months=6
    ) -> BacktestResultList:
        if self.parameters and len(self.strategies) != len(self.parameters):
            raise RuntimeError()
        backtest_results = BacktestResultList()
        for idx, strategy in enumerate(self.strategies):
            for symbol in self.ticker_symbols:
                logger.debug(f"Processing {symbol}")
                parameter = self.parameters[idx]
                df = self.get_data(symbol, history_months)
                # check if the dataframe is empty
                if df.empty:
                    logger.warning(f"Empty dataframe for {symbol}")
                    continue
                # add time measurement
                start_time = datetime.now()
                result = self.run_implementation(
                    strategy, symbol, df, commission, cash, parameter
                )
                elapsed_time = datetime.now() - start_time
                if result is None:
                    logger.warning(f"Empty result for {symbol}")
                    continue
                elif isinstance(
                    result, tuple
                ):  # if the result is a tuple, we have an overall result and a last result
                    last_result, overall_result = result
                    backtest_results.append(last_result)
                    backtest_results.append(overall_result)
                else:
                    result.time_taken = elapsed_time.total_seconds()
                    backtest_results.append(result)
        return backtest_results

    def run_implementation(
        self,
        strategy: BaseStrategy,
        symbol: str,
        df: pd.DataFrame,
        commission: float,
        cash: float,
        parameter: dict,
    ) -> BacktestResult:
        strategy.set_parameters(strategy, parameter)
        start_time = datetime.now()
        bt = Backtest(
            df,
            strategy,
            commission=commission,
            cash=cash,
            trade_on_close=True,
            exclusive_orders=True,
        )
        result = bt.run()
        time_taken = (datetime.now() - start_time).total_seconds()
        return BacktestResult.from_stats_pd(symbol, result, bt, time_taken)
