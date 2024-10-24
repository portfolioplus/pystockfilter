# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas_ta as ta
import pandas as pd

from pystockfilter.strategy.base_strategy import BaseStrategy


class DojiRsiStrategy(BaseStrategy):
    para_rsi_period = 14
    para_confirmation_threshold = 1  # Percent change for confirmation

    def init(self):
        # Use a single _algo function to calculate Doji, RSI, and other indicators
        self.doji, self.rsi, self.close = self.I(
            DojiRsiStrategy._algo,
            self.data,  # DataFrame containing Open, High, Low, Close, Volume, etc.
            self.para_rsi_period,
            self.para_confirmation_threshold,
            overlay=False,
        )

        # Store last Doji index for confirmation
        self.last_doji_index = None

        super().setup(
            buy_signal=self.buy_condition,
            sell_signal=self.sell_condition,
        )

    @staticmethod
    def _algo(
        data: pd.DataFrame, para_rsi_period: int, para_confirmation_threshold: float
    ):
        """
        The _algo function calculates multiple indicators using the input DataFrame (data) and parameters.
        - Doji pattern
        - RSI
        - Close prices (passed through directly for convenience)
        """
        # Extract OHLC data from the DataFrame
        open_ = pd.Series(data.Open)
        high = pd.Series(data.High)
        low = pd.Series(data.Low)
        close = pd.Series(data.Close)

        # Doji pattern detection
        doji = ta.cdl_doji(open_, high, low, close)

        # RSI calculation
        rsi = ta.rsi(close, para_rsi_period)

        # Return the calculated indicators in a dictionary
        return doji, rsi, close

    def is_divergence(self, current_price, current_rsi, previous_price, previous_rsi):
        """
        Detect divergence: Price and RSI moving in opposite directions.
        A bullish divergence occurs when the price is making lower lows but RSI makes higher lows.
        A bearish divergence occurs when the price is making higher highs but RSI makes lower highs.
        """
        if previous_price is None or previous_rsi is None:
            return False

        # Bullish divergence: price makes lower low, RSI makes higher low
        if current_price < previous_price and current_rsi > previous_rsi:
            return True

        # Bearish divergence: price makes higher high, RSI makes lower high
        if current_price > previous_price and current_rsi < previous_rsi:
            return True

        return False

    def buy_condition(self):
        # Buy when a Doji forms, there is a bullish divergence with RSI, and the next candle confirms the reversal (i.e., bullish).
        if self.doji != 0:
            self.last_doji_index = self
            return False

        if self.last_doji_index is not None:
            previous_close = self.close[self.last_doji_index]
            previous_rsi = self.rsi[self.last_doji_index]
            current_close = self.close
            current_rsi = self.rsi

            # Check for bullish divergence
            if self.is_divergence(
                current_close, current_rsi, previous_close, previous_rsi
            ):
                # Wait for confirmation: the current close must be higher than the Doji close
                if current_close > previous_close * (
                    1 + self.para_confirmation_threshold / 100
                ):
                    return True

        return False

    def sell_condition(self):
        # Sell when a Doji forms, there is a bearish divergence with RSI, and the next candle confirms the reversal (i.e., bearish).
        if self.doji != 0:
            self.last_doji_index = len(self.close) - 1
            return False

        if self.last_doji_index is not None:
            previous_close = self.close[self.last_doji_index]
            previous_rsi = self.rsi[self.last_doji_index]
            current_close = self.close
            current_rsi = self.rsi

            # Check for bearish divergence
            if self.is_divergence(
                current_close, current_rsi, previous_close, previous_rsi
            ):
                # Wait for confirmation: the current close must be lower than the Doji close
                if current_close < previous_close * (
                    1 - self.para_confirmation_threshold / 100
                ):
                    return True

        return False

    @staticmethod
    def get_optimizer_parameters() -> dict:
        def constraint(p):
            return p.para_rsi_period > 0

        return {
            "para_rsi_period": range(2, 50, 1),
            "para_confirmation_threshold": range(
                0, 5, 1
            ),  # Confirmation within 0-5% move
            "constraint": constraint,
        }
