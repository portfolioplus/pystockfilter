# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy

from backtesting.test import SMA


class RSIStrategy(BaseStrategy):
    para_rsi_window = 5
    para_rsi_enter = 60
    para_rsi_exit = 50

    @staticmethod
    def algo(data, window: int):
        close = pd.Series(data.Close)
        rsi = ta.rsi(close, window)
        return rsi

    def init(self):
        self.rsi = self.I(RSIStrategy.algo, self.data, self.para_rsi_window)

    def next(self):
        if self.rsi > self.para_rsi_enter:
            self.buy()
        elif self.rsi < self.para_rsi_exit:
            self.sell()
