# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
from datetime import datetime
import numpy as np
import pandas as pd


class BaseFilter:
    """
    Base Class for autotrader filter
    """

    SELL = 0
    HOLD = 1
    BUY = 2

    def __init__(self, arguments, logger: logging.Logger):
        self.logger = logger
        self.need_bars = arguments["bars"]
        self.now_date = arguments.get("now_date", datetime.today())
        self.need_index_bars = arguments["index_bars"]
        self.args = arguments["args"]
        self.name = arguments["name"]
        self.calc = 0

    def set_parameter(self, parameter: dict):
        """
        Sets the parameter for the filter
        :param parameter: dictionary with parameter
        :return: nothing
        """
        raise NotImplementedError()

    def run(self, pandas_df: pd.DataFrame, parameter: dict):
        """
        Runs the filter
        :param pandas_series: pandas series
        :param parameter: dictionary with parameter
        :return: nothing
        """
        self.bars = pandas_df
        self.set_parameter(parameter)
        return self.analyse()

    def analyse(self):
        """
        Starts analysis process
        :return:
        """
        if self.calc >= self.buy:
            return BaseFilter.BUY
        elif self.calc <= self.sell:
            return BaseFilter.SELL
        return BaseFilter.HOLD

    def get_calculation(self):
        """
        Returns the calculation of analysis
        :return: calculated value
        """
        raise NotImplementedError

    def look_back_date(self):
        """
        Returns the look back date
        :return: look back in months
        """
        raise NotImplementedError

    def set_bars(self, bars):
        """
        Setter method for bar
        :param bars:
        :return: nothing
        """
        # convert to numpy
        # rename columns to lower case

        self.bars = self.convert_bars(bars)

    @staticmethod
    def convert_bars(bars):
        """
        Converts bars to numpy array
        :param bars:
        :return: numpy array
        """
        # convert list to pandas df
        df = pd.DataFrame(
            [[i.close, i.open, i.volume, i.high, i.low, i.date] for i in bars],
            columns=["Close", "Open", "Volume", "High", "Low", "Date"],
        )
        return df

    def set_index_bars(self, bars):
        """
        Setter method for index bar
        :param bars:
        :return: nothing
        """
        # convert to numpy
        self.index_bars = self.convert_bars(bars)

    def set_stock(self, stock):
        """
        Setter for stock
        :param stock: db object
        :return: nothing
        """
        self.stock = stock
