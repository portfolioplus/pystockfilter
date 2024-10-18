# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy

from pystockfilter.backtesting.lib import crossover


class UltimateStrategy(BaseStrategy):
    para_uo_short = 7
    para_uo_medium = 14
    para_uo_long = 28
    para_uo_upper = 70
    para_uo_lower = 30

    @staticmethod
    def _algo(data, para_uo_short: int, para_uo_medium: int, para_uo_long: int):
        close = pd.Series(data.Close)
        high = pd.Series(data.High)
        low = pd.Series(data.Low)
        ultimate = ta.uo(
            close,
            high,
            low,
            para_uo_short,
            para_uo_medium,
            para_uo_long,
            para_uo_short,
            para_uo_medium,
            para_uo_long,
        )
        return ultimate

    def init(self):
        self.uo = self.I(
            UltimateStrategy.algo,
            self.data,
            self.para_uo_short,
            self.para_uo_medium,
            self.para_uo_long,
            name=f"UO({self.para_uo_short}, {self.para_uo_medium}, {self.para_uo_long})",
            overlay=True,
        )
        self.close = self.I(lambda x: x.Close, self.data)
        # create thresholds for buy and sell signals
        self.uo_upper = self.I(
            UltimateStrategy.algo_threshold,
            self.para_uo_upper,
            len(self.data),
            name=f"Buy ({self.para_uo_upper})",
            overlay=True,
        )
        self.uo_lower = self.I(
            UltimateStrategy.algo_threshold,
            self.para_uo_lower,
            len(self.data),
            name=f"Sell ({self.para_uo_lower})",
            overlay=True,
        )
        self.setup(
            sell_signal=lambda: crossover(self.uo, self.uo_upper),
            buy_signal=lambda: crossover(self.uo_lower, self.uo),
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint_uo(p):
            return (
                (p.para_uo_upper > p.para_uo_lower)
                and (p.para_uo_upper - p.para_uo_lower) > 10
                and (p.para_uo_long > p.para_uo_medium > p.para_uo_short)
                and (p.para_uo_long - p.para_uo_medium) > 5
                and (p.para_uo_medium - p.para_uo_short) > 3
            )

        return {
            "para_uo_short": range(7, 30, 1),
            "para_uo_medium": range(14, 40, 1),
            "para_uo_long": range(28, 80, 1),
            # "para_uo_upper": range(20, 100, 1),
            # "para_uo_lower": range(-30, 50, 1),
            "constraint": constraint_uo,
        }
