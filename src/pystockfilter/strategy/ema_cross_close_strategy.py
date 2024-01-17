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


class EmaCrossCloseStrategy(BaseStrategy):
    para_ema = 14

    def init(self):
        self.ema = self.I(EmaCrossCloseStrategy.algo_ema, self.data, self.para_ema)
        self.close = self.I(lambda x: x.Close, self.data)

    @staticmethod
    def algo_ema(data, window: int):
        close = pd.Series(data.Close)
        ema = ta.ema(close, window)
        return ema

    def next(self):
        if crossover(self.ema, self.close):
            self.buy()
        elif crossover(self.close, self.ema):
            self.sell()
