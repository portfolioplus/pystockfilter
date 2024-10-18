# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.backtesting.lib import crossover


class BollingerVolumeStrategy(BaseStrategy):
    para_bb_window = 20  # Bollinger Bands period
    para_bb_std_dev = 2.0  # Bollinger Bands standard deviation
    para_volume_window = 20  # Volume Moving Average window
    para_volume_multiplier = 1.2  # Volume threshold multiplier for entry confirmation
    caching = True

    @staticmethod
    def _algo(
        data: pd.DataFrame,
        para_bb_window: int,
        para_bb_std_dev: float,
        para_volume_window: float,
    ):
        # Calculate Bollinger Bands
        para_bb_std_dev = float(para_bb_std_dev)
        bbands_df = ta.bbands(
            pd.Series(data.Close), length=para_bb_window, std=para_bb_std_dev
        )
        upper = bbands_df[f"BBU_{para_bb_window}_{para_bb_std_dev}"]
        middle = bbands_df[f"BBM_{para_bb_window}_{para_bb_std_dev}"]
        lower = bbands_df[f"BBL_{para_bb_window}_{para_bb_std_dev}"]
        vol = pd.Series(data.Volume)
        volume_ma = vol.rolling(window=para_volume_window).mean()
        return lower, middle, upper, volume_ma, vol

    def init(self):
        plot = not BollingerVolumeStrategy.caching
        # Define and plot Bollinger Bands and Volume
        self.close = self.I(lambda x: x.Close, self.data, plot=plot)
        low, mid, up, vol_ma, vol = BollingerVolumeStrategy._algo(
            self.data,
            self.para_bb_window,
            self.para_bb_std_dev,
            self.para_volume_window,
        )
        # Bollinger Bands
        self.bb_lower, self.bb_middle, self.bb_upper = self.I(
            lambda x: (x[0], x[1], x[2]),
            (low, mid, up),
            name=f"Bollinger Bands (Window {self.para_bb_window}, Std Dev {self.para_bb_std_dev})",
            plot=plot,
        )
        if self.para_volume_window > 0:
            # Volume and Volume Moving Average
            self.volume, self.volume_ma = self.I(
                lambda x: (x[0], x[1]),
                (vol, vol_ma),
                name=f"Volume & Volume MA({self.para_volume_window})",
                plot=plot,
            )

        # Set up the buy and sell signals based on Bollinger Bands reversal and volume confirmation
        super().setup(
            buy_signal=lambda: crossover(self.close, self.bb_lower)
            and (
                self.para_volume_window == 0
                or (self.volume > self.volume_ma * self.para_volume_multiplier)
            ),
            sell_signal=lambda: crossover(self.close, self.bb_upper)
            and (
                self.para_volume_window == 0
                or (self.volume > self.volume_ma * self.para_volume_multiplier)
            ),
        )

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return (
                p.para_volume_multiplier > 1
                and p.para_bb_std_dev > 0.1
                and p.para_bb_std_dev < 3.1
                and p.para_bb_window > 9
                and p.para_volume_window > 9
            )

        return {
            "para_bb_window": range(10, 50, 1),  # Range of periods for Bollinger Bands
            "para_bb_std_dev": [
                x / 10 for x in range(15, 30)
            ],  # Range of std deviations, e.g., 1.5 to 3.0
            "para_volume_multiplier": [
                x / 10 for x in range(10, 30)
            ],  # e.g., 1.0 to 3.0 times volume
            "para_volume_window": range(10, 50, 1),  # Volume Moving Average window
            "constraint": constraint,
        }
