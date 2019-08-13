# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
import numpy as np


class BaseFilter:
    """
    Base Class for autotrader filter
    """

    SELL = 0
    BUY = 1
    HOLD = 2

    def __init__(self, arguments, logger: logging.Logger):
        self.logger = logger
        self.need_bars = arguments['bars']
        self.need_index_bars = arguments['index_bars']
        self.args = arguments['args']
        self.name = arguments['name']
        self.calc = 0

    def analyse(self):
        """
        Starts analysis process
        :return:
        """
        raise NotImplementedError

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
        self.bars = np.asarray([[i.close,
                                i.open,
                                i.volume,
                                i.high,
                                i.low,
                                i.date] for i in bars])

    def set_index_bars(self, bars):
        """
        Setter method for index bar
        :param bars:
        :return: nothing
        """
        # convert to numpy
        self.index_bars = np.asarray([[i.close,
                                       i.open,
                                       i.volume,
                                       i.high,
                                       i.low,
                                       i.date] for i in bars])

    def set_stock(self, stock):
        """
        Setter for stock
        :param stock: db object
        :return: nothing
        """
        self.stock = stock
