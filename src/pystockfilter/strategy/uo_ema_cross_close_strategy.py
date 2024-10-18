# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""


from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy
from pystockfilter.strategy.uo_strategy import UltimateStrategy

from pystockfilter.backtesting.lib import crossover, cross


class UltimateEmaCrossCloseStrategy(UltimateStrategy):
    para_ema_short = 14

    def init(self):
        super().init()
        self.ema_short = None
        if self.para_ema_short > 0:
            self.ema_short = self.I(
                EmaCrossCloseStrategy.algo,
                self.data.Close,
                self.para_ema_short,
                overlay=True,
                name=f"EMA({self.para_ema_short})",
            )
        self.close = self.I(lambda x: x.Close, self.data)

        self.setup(
            buy_signal=lambda: (
                self.ema_short is None or crossover(self.close, self.ema_short)
            )
            and self.uo > self.uo_upper,
            sell_signal=lambda: (
                self.ema_short is None or cross(self.close, self.ema_short)
            )
            and self.uo_lower > self.uo,
        )
