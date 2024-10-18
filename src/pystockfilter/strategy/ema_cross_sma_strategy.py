# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy
from pystockfilter.strategy.sma_cross_sma_strategy import SmaCrossSmaStrategy
from pystockfilter.backtesting.lib import crossover, cross


class EmaCrossSmaStrategy(EmaCrossCloseStrategy):
    para_sma_short = 26

    def init(self):
        super().init()
        self.sma_short = self.I(
            SmaCrossSmaStrategy.algo,
            self.data.Close,
            self.para_sma_short,
            overlay=True,
            name=f"SMA({self.para_sma_short})",
        )
        super().setup(
            buy_signal=lambda: crossover(self.sma_short, self.ema_short),
            sell_signal=lambda: cross(self.ema_short, self.sma_short),
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return (
                p.para_sma_short > p.para_ema_short
                and (p.para_sma_short - p.para_ema_short) > 10
            )

        return {
            "para_ema": range(2, 50, 1),  # Realistic range for short EMA
            "para_sma": range(10, 150, 1),  # Realistic range for SMA
            "constraint": constraint,
        }
