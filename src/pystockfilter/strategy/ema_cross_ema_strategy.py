# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy
from pystockfilter.backtesting.lib import crossover, cross


class EmaCrossEmaStrategy(EmaCrossCloseStrategy):
    para_ema_long = 26

    def init(self):
        super().init()
        self.ema_long = self.I(
            EmaCrossCloseStrategy.algo,
            self.data.Close,
            self.para_ema_long,
            overlay=True,
            name=f"EMA({self.para_ema_long})",
        )
        super().setup(
            buy_signal=lambda: crossover(self.ema_long, self.ema_short),
            sell_signal=lambda: cross(self.ema_short, self.ema_long),
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p: EmaCrossEmaStrategy):
            return (
                p.para_ema_long > p.para_ema_short
                and (p.para_ema_long - p.para_ema_short) > 7
            )

        return {
            "para_ema_short": range(2, 50, 1),
            "para_ema_long": range(10, 150, 1),
            "constraint": constraint,
        }
