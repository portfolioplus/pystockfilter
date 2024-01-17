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


class SmaCrossSmaStrategy(BaseStrategy):
    para_sma = 14

    def init(self):
        self.sma = self.I(SmaCrossSmaStrategy.algo_sma, self.data, self.para_sma)
        self.close = self.I(lambda x: x.Close, self.data)

    @staticmethod
    def algo_sma(data, window: int):
        close = pd.Series(data.Close)
        sma = ta.sma(close, window)
        return sma

    def next(self):
        if crossover(self.sma, self.close):
            self.buy()
        elif crossover(self.close, self.sma):
            self.sell()
