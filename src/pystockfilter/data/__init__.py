# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
class StockDataSource:

    @staticmethod
    def get_stock_data(symbol: str, start: str, end: str, **kwargs):
        raise NotImplementedError()
