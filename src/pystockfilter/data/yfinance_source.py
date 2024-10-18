# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from datetime import datetime
import yfinance as yf

from pystockfilter.data import StockDataSource
import pandas as pd

class YFinanceDataSource(StockDataSource):
    
    @staticmethod
    def get_stock_data(symbol: str, start: datetime, end: datetime):
        data = yf.download(symbol, start=start, end=end)
        # Check if the columns are a MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            # Select the price type (Open, Close, etc.) from the MultiIndex
            data.columns = data.columns.get_level_values(0)
        return data