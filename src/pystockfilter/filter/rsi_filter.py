# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
import numpy as np
import pandas_ta as ta
import pandas as pd
from dateutil.relativedelta import relativedelta

from pystockfilter.filter.base_filter import BaseFilter
from pystockfilter.tool.helper import float_range_list


class RsiFilter(BaseFilter):
    """
    The RSI Filter says trust other indicators
    when threshold of 70 have been reached.
    """

    NAME = "RsiFilter"
    optimize_parameter = {
        "parameter": range(4, 20, 1),
        "threshold_buy": float_range_list(60.0, 95.0, 5.0),
        "threshold_sell": float_range_list(20.0, 45.0, 5.0),
        "constraint": lambda p: p.threshold_sell < p.threshold_buy,
    }

    def __init__(self, arguments: dict, logger: logging.Logger):
        self.buy = arguments["args"]["threshold_buy"]
        self.sell = arguments["args"]["threshold_sell"]
        self.lookback = arguments["args"]["lookback"]
        self.parameter = arguments["args"]["parameter"]
        super(RsiFilter, self).__init__(arguments, logger)

    def set_parameter(self, parameter: dict):
        buy = parameter.get("threshold_buy", None)
        if buy is not None:
            self.buy = buy
        sell = parameter.get("threshold_sell", None)
        if sell is not None:
            self.sell = sell
        parameter = parameter.get("parameter", None)
        if parameter is not None:
            self.parameter = parameter

    def analyse(self):
        if not (self.bars.size - self.parameter > 0):
            raise RuntimeError
        my_result = ta.rsi(self.bars, self.parameter)
        median = my_result.median()
        if not np.isnan(median):
            self.calc = float(median)
        else:
            self.logger.warning("Data causes nan. {}".format(self.bars))
        return super(RsiFilter, self).analyse()

    def get_calculation(self):
        return self.calc

    def look_back_date(self):
        return self.now_date + relativedelta(months=-self.lookback)
