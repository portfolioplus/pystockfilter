# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from datetime import datetime
from types import SimpleNamespace
from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args
from typing import Dict
from pystockfilter.data import StockDataSource
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.result import BacktestResult, BacktestResultList
from pystockfilter.tool.start_base import StartBase
from pystockfilter import logger
import multiprocessing as mp


class StartBatchOptimizer(StartBase):

    def __init__(
        self,
        ticker_symbols: list[str],
        strategies: list[BaseStrategy],
        optimizer_parameters: list[dict],
        data_source: StockDataSource,
        max_tries: int = None,
    ):
        super().__init__(ticker_symbols, strategies, optimizer_parameters, data_source)
        self.ticker_symbols_data = {}
        self.max_tries = max_tries

    @staticmethod
    def median(lst):
        n = len(lst)
        s = sorted(lst)
        return (s[n // 2] + s[~n // 2]) / 2

    @staticmethod
    def mean(lst):
        return sum(lst) / len(lst)

    def define_parameter_space(self, parameter_dict: dict):
        """
        Convert optimizer parameter dictionary to skopt parameter space,
        assuming each `para_` parameter is a range or list.
        """
        space = []
        for param_name, param_range in filter(
            lambda x: x[0].startswith("para_"), parameter_dict.items()
        ):
            if isinstance(param_range, range):
                # Integer range parameter
                space.append(
                    Integer(min(param_range), max(param_range), name=param_name)
                )
            elif isinstance(param_range, list):
                # Categorical options if it's a list
                space.append(Categorical(param_range, name=param_name))
            else:
                logger.warning(
                    f"Unsupported parameter range type for {param_name}: {param_range}"
                )

        return space

    def bayesian_optimization(
        self,
        idx: int,
        strategy: BaseStrategy,
        commission: float,
        cash: float,
        history_months: int,
        n_calls=50,
    ):
        # Filter parameters starting with "para_"
        parameter_dict = dict(
            filter(lambda x: x[0].startswith("para_"), self.parameters[idx].items())
        )
        constraint = self.parameters[idx].get(
            "constraint", lambda x: True
        )  # Use provided constraint or default to True

        space = self.define_parameter_space(parameter_dict)

        # Define objective function for the optimizer
        @use_named_args(space)
        def objective(**params: Dict):
            # Map params to dictionary format for the strategy
            parameter = {name: params[name] for name in parameter_dict.keys()}
            # Check if the parameter combination satisfies the constraint
            if not constraint(SimpleNamespace(**params)):
                logger.debug(
                    f"Parameter combination {parameter} fails constraint check."
                )
                return 1e6  # Return a high penalty if the constraint is not satisfied

            # Initialize the overall result
            results = []

            # Calculate the backtest result for each symbol
            for symbol in self.ticker_symbols:
                try:
                    result = self.run_parameter_combination(
                        strategy, symbol, commission, cash, history_months, parameter
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(
                        f"Error processing parameter set {parameter} for symbol {symbol}: {e}"
                    )
                    return 1e6  # Return a large penalty if an error occurs

            # Return negative SQN for maximization
            return -StartBatchOptimizer.median(results)

        # Run Bayesian optimization
        res = gp_minimize(objective, space, n_calls=n_calls, random_state=0)

        # Extract the best parameters and log them
        best_params = {dim.name: val for dim, val in zip(space, res.x)}
        logger.info(
            f"Best parameters found for strategy {strategy.__name__}: {best_params} with SQN score: {-res.fun}"
        )
        return best_params

    def run_strategy(
        self,
        idx: int,
        strategy: BaseStrategy,
        commission: float,
        cash: float,
        history_months: int,
    ):
        start_time = datetime.now()
        best_params = self.bayesian_optimization(
            idx, strategy, commission, cash, history_months
        )
        overall_results = BacktestResult(
            "overall", str(strategy.name), best_params, None, None, None, 0.0, 0.0, 0.0
        )
        for symbol in self.ticker_symbols:
            df = self.get_data(symbol, history_months)
            result = self.run_implementation(
                strategy, symbol, df, commission, cash, best_params
            )
            if result is None:
                logger.warning(f"Empty result for {symbol}")
                continue
            overall_results.earnings += result.earnings
            overall_results.sqn += result.sqn
        overall_results.earnings /= len(self.ticker_symbols)
        overall_results.sqn /= len(self.ticker_symbols)
        time_taken = (datetime.now() - start_time).total_seconds()
        overall_results.time_taken = time_taken
        return overall_results

    def run_parameter_combination(
        self, strategy, symbol, commission, cash, history_months, parameter
    ):
        df = self.get_data(symbol, history_months)
        result = self.run_implementation(
            strategy, symbol, df, commission, cash, parameter
        )
        return result.sqn

    def run(
        self, commission=0.002, cash=10000.0, history_months=6
    ) -> BacktestResultList:
        """Runs the optimizer for each strategy and returns a list of backtest results."""
        if self.parameters and len(self.strategies) != len(self.parameters):
            raise RuntimeError("Mismatch between strategies and parameters.")

        backtest_results = BacktestResultList()

        for idx, strategy in enumerate(self.strategies):
            logger.info(f"Starting optimization for strategy {strategy.__name__}")

            # Run optimization for each strategy
            result = self.run_strategy(idx, strategy, commission, cash, history_months)

            # Collect and log the optimized result
            backtest_results.append(result)
            logger.info(
                f"Optimization completed for strategy {strategy.__name__} with SQN: {result.sqn}"
            )

        return backtest_results
