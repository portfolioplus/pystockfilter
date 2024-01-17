# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossEmaStrategy
from pystockfilter.strategy.sma_cross_close_strategy import SmaCrossSmaStrategy
from backtesting.lib import crossover


class SmaCrossEmaStrategy(EmaCrossEmaStrategy):
    para_ema = 5
    para_sma = 14

    def init(self):
        self.ema = self.I(EmaCrossEmaStrategy.algo_ema, self.data, self.para_ema)
        self.sma = self.I(SmaCrossSmaStrategy.algo_sma, self.data, self.para_sma)
        self.close = self.I(lambda x: x.Close, self.data)

    def next(self):
        if crossover(self.ema, self.sma):
            self.buy()
        elif crossover(self.sma, self.ema):
            self.sell()
