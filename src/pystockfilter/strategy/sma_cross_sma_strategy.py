# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from pystockfilter.strategy.sma_cross_close_strategy import SmaCrossCloseStrategy

from pystockfilter.backtesting.lib import crossover, cross


class SmaCrossSmaStrategy(SmaCrossCloseStrategy):
    para_sma_long = 50

    def init(self):
        super().init()
        self.sma_long = self.I(
            SmaCrossSmaStrategy.algo,
            self.data.Close,
            self.para_sma_long,
            overlay=True,
            name=f"SMA({self.para_sma_long})",
        )
        self.setup(
            buy_signal=lambda: crossover(self.sma_long, self.sma_short),
            sell_signal=lambda: cross(self.sma_short, self.sma_long),
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return (
                p.para_sma_long > p.para_sma_short
                and (p.para_sma_long - p.para_sma_short) > 10
            )

        return {
            "para_sma_short": range(5, 30, 1),
            "para_sma_long": range(30, 100, 1),
            "constraint": constraint,
        }
