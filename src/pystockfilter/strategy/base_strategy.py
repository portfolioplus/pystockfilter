# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from collections import OrderedDict
from enum import Enum
from functools import wraps
import uuid
import zlib


import pandas as pd
from pystockfilter.backtesting import Strategy
from pandas.util import hash_pandas_object

from pystockfilter import logger


class Signals(Enum):
    BUY = 1
    SELL = 2
    HOLD = 3


class BaseStrategy(Strategy):
    # Define cache size and storage
    _cache_max_size = 100  # Set max size as needed
    _cache = OrderedDict()
    caching = True

    @staticmethod
    def _threshold(threshold: int, length: int):
        return pd.Series([threshold] * length)

    @classmethod
    def algo_threshold(cls, threshold: int, length: int):
        func = (
            BaseStrategy._threshold
            if not cls.caching
            else cls.cache(BaseStrategy._threshold)
        )
        return func(threshold, length)

    @classmethod
    def algo(cls, *args, **kwargs):
        """General-purpose method to run and cache subclass-specific _algo methods."""
        func = cls._algo if not cls.caching else cls.cache(cls._algo)
        result = func(*args, **kwargs)
        return result

    @classmethod
    def cache(cls, func):
        """Decorator to cache the results of the function based on its arguments."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique cache key based on the function's arguments
            # only take take tow rows at the beginning and two last rows of df to reduce hash caluclation time
            # Directly select the first two and last two rows without appending or concatenation
            if isinstance(args[0], pd.Series):
                sample_data = (
                    args[0].iloc[:2].values.tobytes()
                    + args[0].iloc[-2:].values.tobytes()
                )
                data_hash = zlib.crc32(sample_data)
            elif isinstance(args[0], pd.DataFrame):
                close = args[0].get("Close", args[0].iloc[:, :1])
                sample_data = (
                    close.iloc[:2].values.tobytes() + close.iloc[-2:].values.tobytes()
                )
                data_hash = zlib.crc32(sample_data)
            else:
                # Use a random UUID for non-pandas arguments
                data_hash = uuid.uuid4().int
            cache_key = (func.__name__, data_hash, *args[1:], frozenset(kwargs.items()))

            # Check if result is cached
            if cache_key in cls._cache:
                # Move accessed item to end to mark it as recently used
                cls._cache.move_to_end(cache_key)
                return cls._cache[cache_key]

            # Call the function and cache the result
            result = func(*args, **kwargs)
            cls._cache[cache_key] = result
            cls._cache.move_to_end(cache_key)

            # Enforce cache size limit
            if len(cls._cache) > cls._cache_max_size:
                cls._cache.popitem(last=False)  # Remove the oldest item

            return result

        return wrapper

    @staticmethod
    def get_optimizer_parameters() -> dict:
        raise NotImplementedError("This method must be implemented by the subclass. ")

    def setup(self, sell_signal, buy_signal):
        self.sell_signal = sell_signal
        self.buy_signal = buy_signal
        self.bought = False
        self.profit = 0

    @property
    def name(self):
        return self.__class__.__name__

    def get_parameters(self) -> dict:
        """
        This method returns a dictionary of parameters for the strategy.
        It filters the instance variables of the class, returning only those that start with 'para_'.

        Returns:
            dict: A dictionary where the keys are the parameter names and the values are the parameter values.
        """
        parameters = dict(
            [
                (key, val)
                for key, val in vars(self).items()
                if f"{key}".startswith("para_")
            ]
        )
        return parameters

    @staticmethod
    def set_parameters(strategy, parameters: dict):
        """
        This method sets the parameters of the strategy.
        It iterates through the dictionary and sets the instance variables of the strategy
        to the values in the dictionary.

        Args:
            strategy (Strategy): The strategy to set the parameters for.
            parameters (dict): A dictionary where the keys are the parameter names and the values are the parameter values.
        """
        for key, val in parameters.items():
            setattr(strategy, key, val)

    def next(self):
        if self.is_buy():
            logger.debug(f"Buy signal at {self.data.index[-1]}")
            self.buy()
        elif self.is_sell():
            logger.debug(f"Sell signal at {self.data.index[-1]}")
            self.sell()

    def is_buy(self):
        is_buy = self.buy_signal() and not self.bought
        if is_buy:
            self.bought = True
        return is_buy

    def is_sell(self):
        is_sell = self.sell_signal() and self.bought
        if is_sell:
            self.bought = False
        return is_sell

    def status(self):
        buy_signal = self.buy_signal()
        sell_signal = self.sell_signal()
        if buy_signal:
            return Signals.BUY
        elif sell_signal:
            return Signals.SELL
        else:
            return Signals.HOLD
