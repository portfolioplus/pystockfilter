# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy

from backtesting.lib import crossover


class UltimateStrategy(BaseStrategy):
    para_uo_short = 7
    para_uo_medium = 14
    para_uo_long = 28
    para_uo_upper = 50
    para_uo_lower = -50

    @staticmethod
    def algo_ultimate(data, window_short: int, window_medium: int, window_long: int):
        close = pd.Series(data.Close)
        high = pd.Series(data.High)
        low = pd.Series(data.Low)
        ultimate = ta.uo(
            close,
            high,
            low,
            window_short,
            window_medium,
            window_long,
            window_short,
            window_medium,
            window_long,
        )
        return ultimate

    def init(self):
        self.uo = self.I(
            UltimateStrategy.algo_ultimate,
            self.data,
            self.para_uo_short,
            self.para_uo_medium,
            self.para_uo_long,
        )

    def next(self):
        if self.uo > self.para_uo_upper:
            self.buy()
        elif self.para_uo_lower > self.uo:
            self.sell()
