# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging

from pystockfilter.filter.adx_filter import AdxFilter
from pystockfilter.filter.levermann_score import LevermannScore
from pystockfilter.filter.piotroski_score import PiotroskiScore
from pystockfilter.filter.price_target_score import PriceTargetScore
from pystockfilter.filter.rsi_filter import RsiFilter
from pystockfilter.filter.stock_is_hot import StockIsHot
from pystockfilter.filter.stock_is_hot_secure import StockIsHotSecure
from pystockfilter.tool.build_filters import BuildFilters


class BuildInternalFilters:
    """
    This tool builds all internal filters
    """
    arguments_rsip14 = {
        'name': 'RsiP14',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 70.0,
            'threshold_sell': 70.0,
            'parameter': 14,
            'lookback': 2
        }
    }

    arguments_rsip5 = {
        'name': 'RsiP5',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 70.0,
            'threshold_sell': 70.0,
            'parameter': 5,
            'lookback': 1
        }
    }

    arguments_adxp14 = {
        'name': 'AdxP14',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 30.0,
            'threshold_sell': 30.0,
            'parameter': 14,
            'lookback': 2
        }
    }

    arguments_adxp5 = {
        'name': 'AdxP5',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 30.0,
            'threshold_sell': 30.0,
            'parameter': 5,
            'lookback': 1
        }
    }

    arguments_hot2 = {
        'name': 'StockIsHot2Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'lookback': 2
        }
    }

    arguments_hot3 = {
        'name': 'StockIsHot3Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'lookback': 3
        }
    }

    arguments_hot6 = {
        'name': 'StockIsHot6Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'lookback': 6
        }
    }

    arguments_sec2 = {
        'name': 'SecureHot2Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'secure_value': 0.85,
            'lookback': 2
        }
    }

    arguments_sec3 = {
        'name': 'SecureHot3Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'secure_value': 0.85,
            'lookback': 3
        }
    }

    arguments_sec6 = {
        'name': 'SecureHot6Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'secure_value': 0.85,
            'lookback': 6
        }
    }

    arguments_sech2 = {
        'name': 'SecureHotH2Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'secure_value': 1.2,
            'lookback': 2
        }
    }

    arguments_sech3 = {
        'name': 'SecureHotH3Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'secure_value': 1.25,
            'lookback': 3
        }
    }

    arguments_sech6 = {
        'name': 'SecureHotH6Month',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 0.8,
            'threshold_sell': 0.5,
            'intervals': [7, 30],
            'secure_value': 1.3,
            'lookback': 6
        }
    }

    arguments_pio = {
        'name': 'PiotroskiScore',
        'bars': False,
        'index_bars': False,
        'args': {
            'threshold_buy': 8,
            'threshold_sell': 5,
            'intervals': None,
            'lookback': None
        }
    }

    arguments_lev = {
        'name': 'LevermannScore',
        'bars': True,
        'index_bars': True,
        'args': {
            'threshold_buy': 7,
            'threshold_sell': 2,
            'intervals': None,
            'lookback': 12
        }
    }

    arguments_pri = {
        'name': 'PriceTargetScore',
        'bars': True,
        'index_bars': False,
        'args': {
            'threshold_buy': 8,
            'threshold_sell': -2,
            'intervals': None,
            'lookback': 2
        }
    }

    def __init__(self, arguments: dict, logger: logging.Logger):

        arguments["filters"] = [
            AdxFilter(self.arguments_adxp5, logger),
            AdxFilter(self.arguments_adxp14, logger),
            RsiFilter(self.arguments_rsip5, logger),
            RsiFilter(self.arguments_rsip14, logger),
            StockIsHot(self.arguments_hot2, logger),
            StockIsHot(self.arguments_hot3, logger),
            StockIsHot(self.arguments_hot6, logger),
            StockIsHotSecure(self.arguments_sec2, logger),
            StockIsHotSecure(self.arguments_sec3, logger),
            StockIsHotSecure(self.arguments_sec6, logger),
            StockIsHotSecure(self.arguments_sech2, logger),
            StockIsHotSecure(self.arguments_sech3, logger),
            StockIsHotSecure(self.arguments_sech6, logger),
            PiotroskiScore(self.arguments_pio, logger),
            LevermannScore(self.arguments_lev, logger),
            PriceTargetScore(self.arguments_pri, logger)
        ]
        self.builder = BuildFilters(arguments, logger)

    def build(self):
        """
        Starts the build process for internal filters
        :return: nothing
        """
        return self.builder.build()
