# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from datetime import datetime, timedelta
from pystockfilter.data.yfinance_source import YFinanceDataSource
from joblib import Memory
from pystockfilter import logger

# Setup caching directory
cache_dir = './yfinance_cache'
memory = Memory(cache_dir, verbose=0)


class YFinanceDataSourceCache(YFinanceDataSource):
    
    @staticmethod
    def get_stock_data(symbol: str, start: datetime, end: datetime):
        # round end date to the next day
        end_up = end + timedelta(days=1)
        return YFinanceDataSourceCache.get_stock_data_cache(symbol, start.strftime('%Y-%m-%d'), end_up.strftime('%Y-%m-%d'))
        
    @staticmethod
    @memory.cache
    def get_stock_data_cache(symbol: str, start: str, end: str):
        logger.info(f"Gather data for {symbol} from {start} to {end}")
        return YFinanceDataSource.get_stock_data(symbol, start, end)