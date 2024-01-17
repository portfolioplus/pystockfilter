# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy
from pystockfilter.strategy.base_strategy import BaseStrategy

from backtesting.lib import crossover, cross


class EmaCrossEmaStrategy(BaseStrategy):
    para_ema_short = 14
    para_ema_long = 29

    def init(self):
        self.ema_short = self.I(
            EmaCrossCloseStrategy.algo_ema, self.data, self.para_ema_short
        )
        self.ema_long = self.I(
            EmaCrossCloseStrategy.algo_ema, self.data, self.para_ema_long
        )
        self.close = self.I(lambda x: x.Close, self.data)

    def next(self):
        if crossover(self.ema_short, self.ema_long):
            self.buy()
        elif crossover(self.ema_long, self.ema_short):
            self.sell()
