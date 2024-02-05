# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2023 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from enum import Enum
from backtesting import Strategy

class Signals(Enum):
    BUY = 1
    SELL = 2
    HOLD = 3

class BaseStrategy(Strategy):


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
