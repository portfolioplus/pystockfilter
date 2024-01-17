# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from pystockfilter.data.local_source import LocalDataSource
from pystockfilter.data.pystockdb_source import PyStockDBDataSource
from pystockfilter.data.yfinance_source import YFinanceDataSource
from pystockfilter.data.yfinance_source_cache import YFinanceDataSourceCache


class DataSourceModule:

    Y_FINANCE = 'yfinance'
    Y_FINANCE_CACHE = 'yfinance_cache'
    PY_STOCK_DB = 'pystockdb'
    LOCAL = 'local'

    def __init__(self, source: str, *args, **kwargs):
        if source == DataSourceModule.Y_FINANCE:
            self.data_source = YFinanceDataSource
        elif source == DataSourceModule.PY_STOCK_DB:
            self.data_source = PyStockDBDataSource
        elif source == DataSourceModule.LOCAL:
            self.data_source = LocalDataSource
        elif source == DataSourceModule.Y_FINANCE_CACHE:
            self.data_source = YFinanceDataSourceCache
        else:
            raise ValueError("Unsupported data source")
        # check if option dic is in kwargs
        if 'options' in kwargs:
            options = kwargs['options']
            # set attributes
            for key, value in options.items():
                setattr(self.data_source, key, value)
        # create singleton
        

    def get_stock_data(self, symbol: str, start: str, end: str):
        return self.data_source.get_stock_data(symbol, start, end)