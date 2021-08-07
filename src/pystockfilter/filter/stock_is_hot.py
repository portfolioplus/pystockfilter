# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
import numpy as np
from dateutil.relativedelta import relativedelta

from pystockfilter.filter.base_filter import BaseFilter


class StockIsHot(BaseFilter):
    """
    This filter creates with the help of multiple polyfits in an given date
    range a score for a stock. The value 1 is the best and 0 the worst.
    A stock with a score between 0.75 and 1. shows a good performance.
    """

    NAME = 'StockIsHot'

    def __init__(self, arguments: dict, logger: logging.Logger):
        self.buy = arguments['args']['threshold_buy']
        self.sell = arguments['args']['threshold_sell']
        self.lookback = arguments['args']['lookback']
        self.intervals = arguments['args']['intervals']
        super(StockIsHot, self).__init__(arguments, logger)

    def analyse(self):
        performance_list = []
        for intervals in self.intervals:
            performance_list.append(
                self.get_performance(self.bars[:, 1].astype(np.float64),
                                     intervals)
                )
        ascending_counter = 0
        perf_sum = 0

        for idx, performance in enumerate(performance_list):
            for val in performance:
                perf_sum += (1.0 + idx*4)

                if val >= 0:
                    ascending_counter += (1.0 + idx*4)

        self.calc = (ascending_counter / perf_sum)
        self.logger.debug("Calculated performance is '%f'." % self.calc)
        return super(StockIsHot, self).analyse()

    def get_calculation(self):
        return self.calc

    @staticmethod
    def get_performance(array, interval: int):
        """
        Splits values by interval and calculates for each split the
        performance value
        :param array: close prices of stock
        :param interval: interval in days
        :return: list with performance values
        """
        array = array[array != np.array(None)].astype(np.float64)
        steps = int(array.shape[0]/interval)
        delta_list = np.zeros(steps)
        for idx in range(1, steps+1):
            y_values = array[interval*idx-interval:interval*idx]
            x_values = np.arange(y_values.shape[0])
            poly = np.polyfit(x_values, y_values, 1)
            delta_list[idx-1] = poly[0]
        return np.diff(delta_list)

    def look_back_date(self):
        return self.now_date + relativedelta(months=-self.lookback)
