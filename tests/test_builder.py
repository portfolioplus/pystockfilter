#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
import os
import unittest
from datetime import datetime
from shutil import copyfile

from dateutil.relativedelta import relativedelta
from pony.orm import db_session
from pystockdb.db.schema.stocks import Index, Price, Signal, Stock, Tag, db

import sys

sys.path.insert(0, 'src')

from pystockfilter.base.base_helper import BaseHelper
from pystockfilter.filter.base_filter import BaseFilter
from pystockfilter.filter.adx_filter import AdxFilter
from pystockfilter.filter.levermann_score import LevermannScore
from pystockfilter.filter.piotroski_score import PiotroskiScore
from pystockfilter.filter.price_target_score import PriceTargetScore
from pystockfilter.filter.rsi_filter import RsiFilter
from pystockfilter.filter.stock_is_hot import StockIsHot
from pystockfilter.filter.stock_is_hot_secure import StockIsHotSecure
from pystockfilter.tool.build_filters import BuildFilters
from pystockfilter.tool.build_internal_filters import BuildInternalFilters


class TesFilterBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(test_dir, 'testdb.sqlite')
        db_path_test = os.path.join(test_dir, 'testdb_tmp.sqlite')
        if os.path.exists(db_path_test):
            os.remove(db_path_test)
        copyfile(db_path, db_path_test)
        arguments = {
            'db_args': {
                'provider': 'sqlite',
                'filename': db_path_test,
                'create_db': False,
            }
        }
        db.bind(**arguments["db_args"])
        db.generate_mapping()

    @db_session
    def test_internal_create(self):
        logger = BaseHelper.setup_logger('test')
        cfg = {
            'symbols': ['ADS.F'],
            # fix date in this way because pony orm can not handel fakedatetime
            'now_date': datetime.strptime('2019-08-07', '%Y-%m-%d'),
        }
        builder = BuildInternalFilters(cfg, logger)
        self.assertEqual(builder.build(), 0)
        signal = Signal.select(
            lambda s: 'PiotroskiScore' in s.item.tags.name
        ).first()
        self.assertTrue(signal is not None)
        self.assertEqual(signal.result.value, 5.0)
        # test build filters with all symbols
        cfg['symbols'] = ['ALL']
        builder = BuildInternalFilters(cfg, logger)
        self.assertEqual(builder.build(), 9)

    def test_build(self):
        """
        Tests filter builder
        :return:
        """
        logger = logging.getLogger('test')
        # create simple filter
        my_filter = StockIsHot(
            {
                'name': 'StockIsHot6Month',
                'bars': True,
                'index_bars': False,
                'args': {
                    'threshold_buy': 0.8,
                    'threshold_sell': 0.5,
                    'intervals': [7, 30],
                    'lookback': 6,
                },
            },
            logger,
        )
        # check missing arguments
        builder = BuildFilters({}, logger)
        self.assertEqual(1, builder.build())
        # check simple build
        builder = BuildFilters(
            {
                'filters': [my_filter],
                'symbols': ['IFX.F'],
                'now_date': datetime(2019, 10, 5, 18, 00),
            },
            logger,
        )
        self.assertEqual(0, builder.build())
        with db_session:
            tag_ctx = Tag.select(
                lambda t: t.name == 'StockIsHot6Month'
            ).count()
            self.assertEqual(1, tag_ctx)

    @db_session
    def __filter_test(self, filter_class, args, result):
        logger = logging.getLogger('test')
        fil = filter_class(args, logger)
        if fil.lookback and fil.need_bars:
            fil.set_bars(self.get_bars('IFX.F', fil))
        if fil.lookback and fil.need_index_bars:
            fil.set_index_bars(self.get_index_bars('IFX.F', fil))
        stock = Stock.select(
            (lambda s: 'IFX.F' in s.price_item.symbols.name)
        ).first()
        fil.set_stock(stock)
        strategy_status = fil.analyse()
        strategy_value = fil.get_calculation()
        self.assertEqual(strategy_status, result[0])
        self.assertAlmostEqual(strategy_value, result[1], 2)

    def test_stock_is_hot(self):
        args = {
            'name': 'StockIsHot',
            'bars': True,
            'index_bars': False,
            'args': {
                'threshold_buy': 0.8,
                'threshold_sell': 0.5,
                'intervals': [7, 30],
                'lookback': 6,
            },
        }
        self.__filter_test(StockIsHot, args, [BaseFilter.HOLD, 0.5625])

    def test_stock_is_hot_secure(self):
        args = {
            'name': 'StockIsHotSec',
            'bars': True,
            'index_bars': False,
            'args': {
                'threshold_buy': 0.8,
                'threshold_sell': 0.5,
                'intervals': [7, 30],
                'lookback': 6,
                'secure_value': 7,
            },
        }
        self.__filter_test(StockIsHotSecure, args, [BaseFilter.SELL, 0.38])

    def test_adx(self):
        args = {
            'name': 'adx',
            'bars': True,
            'index_bars': False,
            'args': {
                'threshold_buy': 0.8,
                'threshold_sell': 0.5,
                'intervals': [7, 30],
                'lookback': 6,
                'parameter': 5,
            },
        }
        self.__filter_test(AdxFilter, args, [BaseFilter.BUY, 43.26])

    def test_rsi(self):
        args = {
            'name': 'rsi',
            'bars': True,
            'index_bars': False,
            'args': {
                'threshold_buy': 0.8,
                'threshold_sell': 0.5,
                'intervals': [7, 30],
                'lookback': 6,
                'parameter': 5,
            },
        }
        self.__filter_test(RsiFilter, args, [BaseFilter.BUY, 51.71])

    def test_piotroski(self):
        args = {
            'name': 'pio',
            'bars': False,
            'index_bars': False,
            'args': {'threshold_buy': 8, 'threshold_sell': -2,},
        }
        self.__filter_test(PiotroskiScore, args, [BaseFilter.HOLD, 6])

    def test_levermann(self):
        args = {
            'name': 'lev',
            'bars': True,
            'index_bars': True,
            'args': {'threshold_buy': 7, 'threshold_sell': 2, 'lookback': 12},
        }
        self.__filter_test(LevermannScore, args, [BaseFilter.SELL, -1])

    def test_price_target_score(self):
        args = {
            'name': 'price',
            'bars': True,
            'index_bars': False,
            'args': {'threshold_buy': 8, 'threshold_sell': -2, 'lookback': 1},
        }
        self.__filter_test(PriceTargetScore, args, [BaseFilter.SELL, -4])

    @db_session
    def get_bars(self, symbol, my_filter):
        now = datetime.strptime('2019-07-30', '%Y-%m-%d')
        before = now + relativedelta(months=-my_filter.lookback)
        bars = Price.select(
            lambda p: p.symbol.name == symbol
            and p.date >= before
            and p.date <= now
        )
        return bars

    @db_session
    def get_index_bars(self, symbol, my_filter):
        now = datetime.strptime('2019-07-30', '%Y-%m-%d')
        before = now + relativedelta(months=-my_filter.lookback)
        my_index = Index.select(
            lambda i: symbol in i.stocks.price_item.symbols.name
        ).first()

        bars = Price.select(
            lambda p: p.symbol.name in my_index.price_item.symbols.name
            and p.date >= before
            and p.date <= now
        )
        return bars


if __name__ == "__main__":
    unittest.main()
