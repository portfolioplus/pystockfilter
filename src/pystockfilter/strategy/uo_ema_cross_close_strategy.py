# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.uo_strategy import UlimateStrategy

from backtesting.lib import crossover


class UlimateEmaCrossCloseStrategy(UlimateStrategy):
    para_ema = 14

    def init(self):
        self.uo = self.I(
            UlimateStrategy.algo_ultimate,
            self.data,
            self.para_uo_short,
            self.para_uo_medium,
            self.para_uo_long,
        )
        self.ema = self.I(
            UlimateEmaCrossCloseStrategy.algo_ema, self.data, self.para_ema
        )
        self.close = self.I(lambda x: x.Close, self.data)

    @staticmethod
    def algo_ema(data, window: int):
        close = pd.Series(data.Close)
        ema = ta.ema(close, window)
        return ema

    def next(self):
        in_range = self.para_uo_upper > self.uo > self.para_uo_lower
        if in_range and crossover(self.ema, self.close):
            self.buy()
        elif crossover(self.close, self.ema):
            self.sell()
