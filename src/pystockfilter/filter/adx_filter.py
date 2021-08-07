# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import logging
import numpy as np
import tulipy as ti
from dateutil.relativedelta import relativedelta

from pystockfilter.filter.base_filter import BaseFilter


class AdxFilter(BaseFilter):
    """
    The Average Directional Movement Index Filter says trust other indicators
    when threshold of 30 have been reached.
    """

    NAME = 'AdxFilter'

    def __init__(self, arguments: dict, logger: logging.Logger):
        self.buy = arguments['args']['threshold_buy']
        self.sell = arguments['args']['threshold_sell']
        self.lookback = arguments['args']['lookback']
        self.parameter = arguments['args']['parameter']
        super(AdxFilter, self).__init__(arguments, logger)

    def analyse(self):

        close = self.bars[:, 0].copy(order='C').astype('float64')
        high = self.bars[:, 3].copy(order='C').astype('float64')
        low = self.bars[:, 4].copy(order='C').astype('float64')
        if not (close.size + 2 - 2 * self.parameter > 0):
            raise RuntimeError
        my_result = ti.adx(high, low, close, self.parameter)
        median = np.median(my_result)
        if not np.isnan(median):
            self.calc = float(median)
        else:
            self.logger.warning("Data causes nan. {}".format(close))
        return super(AdxFilter, self).analyse()

    def get_calculation(self):
        return self.calc

    def look_back_date(self):
        return self.now_date + relativedelta(months=-self.lookback)
