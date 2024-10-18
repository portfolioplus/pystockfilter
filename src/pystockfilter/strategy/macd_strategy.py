# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas as pd
import pandas_ta as ta

from pystockfilter.strategy.base_strategy import BaseStrategy

from pystockfilter.backtesting.lib import crossover


class MACDStrategy(BaseStrategy):
    para_macd_fast = 12
    para_macd_slow = 26
    para_macd_signal = 9
    caching = True

    @staticmethod
    def _algo(
        data: pd.Series, para_macd_fast: int, para_macd_slow: int, para_macd_signal: int
    ):
        macd = ta.macd(data, para_macd_fast, para_macd_slow, para_macd_signal)
        return macd

    def init(self):
        plot = not MACDStrategy.caching
        # create thresholds for buy and sell signals
        self.close = self.I(lambda x: x.Close, self.data, plot=plot)
        self.macd_line, self.macd_histogram, self.macd_signal = self.I(
            MACDStrategy.algo,
            pd.Series(self.data.Close),
            self.para_macd_fast,
            self.para_macd_slow,
            self.para_macd_signal,
            overlay=True,
            name=f"MACD({self.para_macd_fast},{self.para_macd_slow}, {self.para_macd_signal})",
            plot=plot,
        )

        # Define buy and sell signals based on MACD crossover
        self.setup(
            buy_signal=lambda: crossover(
                self.macd_line, self.macd_signal
            ),  # MACD crosses above Signal line
            sell_signal=lambda: crossover(
                self.macd_signal, self.macd_line
            ),  # MACD crosses below Signal line
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return (
                p.para_macd_fast < p.para_macd_slow
                and p.para_macd_fast < p.para_macd_signal
                and p.para_macd_slow - p.para_macd_fast >= 5
                and p.para_macd_signal > p.para_macd_fast  # Ensure signal > fast
            )

        return {
            "para_macd_fast": range(5, 20, 1),
            "para_macd_slow": range(15, 40, 1),
            "para_macd_signal": range(5, 20, 1),
            "constraint": constraint,
        }
