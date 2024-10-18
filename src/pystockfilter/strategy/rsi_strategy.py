# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy

from pystockfilter.backtesting.lib import crossover


class RSIStrategy(BaseStrategy):
    para_rsi_window = 14
    para_rsi_enter = 80
    para_rsi_exit = 55
    caching = True

    @staticmethod
    def _algo(data: pd.Series, para_rsi_window: int):
        rsi = ta.rsi(data, para_rsi_window)
        return rsi

    def init(self):
        plot = not RSIStrategy.caching
        # create thresholds for buy and sell signals
        self.close = self.I(lambda x: x.Close, self.data, plot=plot)
        self.rsi_enter = self.I(
            RSIStrategy.algo_threshold,
            self.para_rsi_enter,
            len(self.data.Close),
            name=f"Buy ({self.para_rsi_enter})",
            overlay=True,
            plot=plot,
        )
        self.rsi_exit = self.I(
            RSIStrategy.algo_threshold,
            self.para_rsi_exit,
            len(self.data.Close),
            name=f"Sell ({self.para_rsi_exit})",
            overlay=True,
            plot=plot,
        )
        self.rsi = self.I(
            RSIStrategy.algo,
            pd.Series(self.data.Close),
            self.para_rsi_window,
            overlay=True,
            name=f"RSI({self.para_rsi_window})",
            plot=plot,
        )
        self.setup(
            sell_signal=lambda: crossover(self.rsi, self.rsi_exit),
            buy_signal=lambda: crossover(self.rsi_enter, self.rsi),
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return p.para_rsi_enter < p.para_rsi_exit

        return {
            "para_rsi_window": range(14, 100, 1),
            "para_rsi_enter": range(10, 50, 1),
            "para_rsi_exit": range(50, 90, 1),
            "constraint": constraint,
        }
