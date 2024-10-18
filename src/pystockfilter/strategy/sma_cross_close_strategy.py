# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy

from pystockfilter.backtesting.lib import crossover, cross


class SmaCrossCloseStrategy(BaseStrategy):
    para_sma_short = 14

    def init(self):
        self.sma_short = self.I(
            SmaCrossCloseStrategy.algo,
            self.data.Close,
            self.para_sma_short,
            overlay=True,
            name=f"SMA({self.para_sma_short})",
        )
        self.close = self.I(lambda x: x.Close, self.data)
        self.setup(
            buy_signal=lambda: crossover(self.close, self.sma_short),
            sell_signal=lambda: cross(self.close, self.sma_short),
        )

    @staticmethod
    def _algo(data: pd.Series, para_sma_short: int):
        sma = ta.sma(pd.Series(data), para_sma_short)
        return sma

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return p.para_sma_short > 2

        return {
            "para_sma_short": range(5, 50, 1),
            "constraint": constraint,
        }
