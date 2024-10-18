# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy
from pystockfilter.strategy.uo_ema_cross_close_strategy import (
    UltimateEmaCrossCloseStrategy,
)

from pystockfilter.backtesting.lib import crossover, cross


class UltimateEmaCrossEmaStrategy(UltimateEmaCrossCloseStrategy):
    para_ema_long = 26

    def init(self):
        super().init()
        self.ema_long = None
        if self.para_ema_long > 0:
            self.ema_long = self.I(
                EmaCrossCloseStrategy.algo,
                self.data.Close,
                self.para_ema_long,
                overlay=True,
                name=f"EMA({self.para_ema_long})",
            )
        super().setup(
            buy_signal=lambda: (
                self.para_ema_long == 0 or crossover(self.ema_long, self.ema_short)
            )
            and self.uo > self.uo_upper,
            sell_signal=lambda: (
                self.para_ema_long == 0 or cross(self.ema_short, self.ema_long)
            )
            and self.uo_lower > self.uo,
        )
