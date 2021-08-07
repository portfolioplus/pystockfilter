# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
from dateutil.relativedelta import relativedelta

from pystockfilter.filter.base_filter import BaseFilter


class PriceTargetScore(BaseFilter):
    """
    Price target score filter
    """

    NAME = 'PriceTargetScore'

    def __init__(self, arguments: dict, logger: logging.Logger):
        self.buy = arguments['args']['threshold_buy']
        self.sell = arguments['args']['threshold_sell']
        self.lookback = arguments['args']['lookback']
        super(PriceTargetScore, self).__init__(arguments, logger)

    def analyse(self):
        price_target_score = 0
        prices = self.stock.get_data("recommendation")['priceTarget']
        low = float(prices['low'])
        high = float(prices['high'])
        mean = float(prices['mean'])
        current = self.bars[:, 0][-1]
        diff_low = current - low
        diff_high = current - high
        diff_mean = current - mean
        low_steps = (mean - low) / 10.0
        if low_steps == 0:
            low_steps = 1
        high_steps = (high - mean) / 10.0
        if high_steps == 0:
            high_steps = 1
        if diff_low < 0:
            price_target_score = -1 * abs(int(diff_low/low_steps))
        elif diff_high > 0:
            price_target_score = int(diff_high / high_steps)
        elif diff_mean < 0:
            price_target_score = -1 * \
                abs(int(diff_mean*2 / (low_steps+high_steps)))
        else:
            price_target_score = int(diff_mean*2 / (low_steps+high_steps))
        self.calc = price_target_score

        return super(PriceTargetScore, self).analyse()

    def get_calculation(self):
        return self.calc

    def look_back_date(self):
        return self.now_date + relativedelta(months=-self.lookback)
