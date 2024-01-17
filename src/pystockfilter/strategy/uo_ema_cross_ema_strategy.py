# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from pystockfilter.strategy.uo_ema_cross_close_strategy import (
    UlimateEmaCrossCloseStrategy,
)

from backtesting.lib import crossover


class UlimateEmaCrossEmaStrategy(UlimateEmaCrossCloseStrategy):
    para_ema_long = 100
    para_ema_short = 40

    def init(self):
        self.uo = self.I(
            UlimateEmaCrossEmaStrategy.algo_ultimate,
            self.data,
            self.para_uo_short,
            self.para_uo_medium,
            self.para_uo_long,
        )
        self.ema_short = self.I(
            UlimateEmaCrossEmaStrategy.algo_ema, self.data, self.para_ema_short
        )
        self.ema_long = self.I(
            UlimateEmaCrossEmaStrategy.algo_ema, self.data, self.para_ema_long
        )

    def next(self):
        in_range = self.para_uo_upper > self.uo > self.para_uo_lower
        if in_range and crossover(self.ema_short, self.ema_long):
            self.buy()
        elif crossover(self.ema_long, self.ema_short):
            self.sell()
