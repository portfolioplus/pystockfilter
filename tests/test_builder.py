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

from pystockdb.tools.base import DBBase

from pystockfilter.filter.stock_is_hot import StockIsHot
from pystockfilter.tool.build_filters import BuildFilters


class TesFilterBuilder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'testdb.sqlite')

        arguments = {'db_args': {
            'provider': 'sqlite',
            'filename': db_path,
            'create_db': False
          }
        }
        DBBase(arguments, None)

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
            'args': {
              'threshold_buy': 0.8,
              'threshold_sell': 0.5,
              'intervals': [7, 30],
              'lookback': 6
            }
          },
          logger
          )
        # check missing arguments
        builder = BuildFilters(
          {},
          logger
          )
        self.assertEquals(1, builder.build())
        # check simple build
        builder = BuildFilters(
          {'filters': [my_filter], 'symbols': ['IFX.F']},
          logger
          )
        self.assertEquals(0, builder.build())
        pass


if __name__ == "__main__":
    unittest.main()
