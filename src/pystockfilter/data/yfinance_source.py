# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from datetime import datetime
import yfinance as yf

from pystockfilter.data import StockDataSource

class YFinanceDataSource(StockDataSource):
    
    @staticmethod
    def get_stock_data(symbol: str, start: datetime, end: datetime):
        data = yf.download(symbol, start=start, end=end)
        return data