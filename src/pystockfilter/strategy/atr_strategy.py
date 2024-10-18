# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.backtesting.lib import gt


class ATRStrategy(BaseStrategy):
    para_atr_window = 14
    para_atr_enter = 2.0  # Threshold for entering position based on ATR
    para_atr_exit = 1.0  # Threshold for exiting position based on ATR
    caching = True

    @staticmethod
    def _algo(data: pd.DataFrame, para_atr_window: int):
        # Calculate ATR based on the window parameter
        atr = ta.atr(
            high=pd.Series(data.High),
            low=pd.Series(data.Low),
            close=pd.Series(data.Close),
            length=para_atr_window,
        )
        return atr

    def init(self):
        plot = not ATRStrategy.caching
        # Get close prices and ATR signals
        self.close = self.I(lambda x: x.Close, self.data, plot=plot)
        self.atr_enter = self.I(
            ATRStrategy.algo_threshold,
            self.para_atr_enter,
            len(self.data.Close),
            name=f"Buy (ATR {self.para_atr_enter})",
            plot=plot,
        )
        self.atr_exit = self.I(
            ATRStrategy.algo_threshold,
            self.para_atr_exit,
            len(self.data.Close),
            name=f"Sell (ATR {self.para_atr_exit})",
            plot=plot,
        )
        self.atr = self.I(
            ATRStrategy._algo,
            self.data,
            self.para_atr_window,
            name=f"ATR({self.para_atr_window})",
            plot=plot,
        )

        # Set up the buy and sell signals based on ATR crossover thresholds
        super().setup(
            buy_signal=lambda: gt(self.atr, self.atr_enter),
            sell_signal=lambda: gt(self.atr_exit, self.atr),
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return (
                p.para_atr_enter > p.para_atr_exit
            )  # Enter threshold should be above exit

        return {
            "para_atr_window": range(10, 50, 1),
            "para_atr_enter": [x / 10 for x in range(10, 50)],  # e.g., 1.0 to 5.0
            "para_atr_exit": [x / 10 for x in range(5, 25)],  # e.g., 0.5 to 2.5
            "constraint": constraint,
        }
