# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
from dateutil.relativedelta import relativedelta

from pystockfilter.filter.base_filter import BaseFilter
from pystockfilter.filter.stock_is_hot import StockIsHot


class StockIsHotSecure(StockIsHot):
    """
    This filter creates with the help of multiple polyfits in an
    given date range a score for a stock. The value 1 is the best
    and 0 the worst.

    A stock with a score between 0.75 and 1. shows a good performance.
    """

    NAME = 'StockIsHotSecure'

    def __init__(self, arguments: dict, logger: logging.Logger):
        self.secure_value = arguments['args']["secure_value"]
        super(StockIsHotSecure, self).__init__(arguments, logger)

    def analyse(self):
        first_value = self.bars[:, 1][0]
        last_value = self.bars[:, 1][-1]
        if first_value == 0:
            return BaseFilter.HOLD
        secure_value = last_value/first_value
        # The stock shows strong losses over a longer period of time.
        # So we decrease the score.
        self.bars = self.bars[:][int(len(self.bars) / 2):]
        status = super(StockIsHotSecure, self).analyse()
        if secure_value > self.secure_value:
            return status
        self.calc = self.calc/2
        return BaseFilter.analyse(self)

    def look_back_date(self):
        return self.now_date + relativedelta(months=-self.lookback*2)
