# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.backtesting.lib import crossover


class MovingAverageRSIStrategy(BaseStrategy):
    para_ma_short = 9  # Short Moving Average window
    para_ma_long = 21  # Long Moving Average window
    para_rsi_window = 14  # RSI window
    para_rsi_threshold = 50  # RSI threshold for trend confirmation
    caching = True

    @staticmethod
    def _algo(data: pd.DataFrame, short_window: int, long_window: int, rsi_window: int):
        # Calculate short, long moving averages and rsi
        short_ma = ta.sma(pd.Series(data.Close), length=short_window)
        long_ma = ta.sma(pd.Series(data.Close), length=long_window)
        rsi = ta.rsi(pd.Series(data.Close), length=rsi_window)
        return short_ma, long_ma, rsi

    def init(self):
        plot = not MovingAverageRSIStrategy.caching
        # Get close prices and MA/RSI signals
        self.close = self.I(lambda x: x.Close, self.data, plot=plot)

        self.short_ma, self.long_ma, self.rsi = self.I(
            MovingAverageRSIStrategy._algo,
            self.data,
            self.para_ma_short,
            self.para_ma_long,
            self.para_rsi_window,
            name=f"Short ({self.para_ma_short}) & Long ({self.para_ma_long}) MAs & RSI({self.para_rsi_window})",
            plot=plot,
        )

        # Set up the buy and sell signals based on MA crossover and RSI confirmation
        super().setup(
            buy_signal=lambda: crossover(self.short_ma, self.long_ma)
            and (self.para_rsi_window == 0 or (self.rsi[-1] > self.para_rsi_threshold)),
            sell_signal=lambda: crossover(self.long_ma, self.short_ma)
            or (self.para_rsi_window == 0 and (self.rsi[-1] < self.para_rsi_threshold)),
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            # Ensure short MA is less than long MA
            return p.para_short_ma < p.para_long_ma and p.para_rsi_threshold in range(
                30, 70
            )

        return {
            "para_short_ma": range(5, 20, 1),  # Short MA between 5 and 20 days
            "para_long_ma": range(15, 50, 1),  # Long MA between 15 and 50 days
            "para_rsi_window": range(10, 20, 1),  # RSI window between 10 and 20 days
            "para_rsi_threshold": range(
                40, 60, 1
            ),  # RSI threshold for trend confirmation
            "constraint": constraint,
        }
