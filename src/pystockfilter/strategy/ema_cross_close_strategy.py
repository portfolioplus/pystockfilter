# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy

from pystockfilter.backtesting.lib import cross, crossover


class EmaCrossCloseStrategy(BaseStrategy):
    para_ema_short = 14

    def init(self):
        self.ema_short = self.I(
            EmaCrossCloseStrategy.algo,
            self.data.Close,
            self.para_ema_short,
            overlay=True,
            name=f"EMA({self.para_ema_short})",
        )
        self.close = self.I(lambda x: x.Close, self.data)

        super().setup(
            buy_signal=lambda: crossover(self.close, self.ema_short),
            sell_signal=lambda: cross(self.ema_short, self.close),
        )

    @staticmethod
    def _algo(data, para_ema_short: int):
        ema = ta.ema(pd.Series(data), para_ema_short)
        return ema

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return p.para_ema_short > 0

        return {
            "para_ema_short": range(2, 50, 1),
            "constraint": constraint,
        }
