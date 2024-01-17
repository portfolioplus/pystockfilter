# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import pandas as pd
from pystockdb.db.schema.stocks import Price

from pystockfilter.data import StockDataSource  # Ensure the correct import for Price

class PyStockDBDataSource(StockDataSource):
    
    @staticmethod
    def get_stock_data(symbol: str, start: str, end: str):
        bars = Price.select(
            lambda p: symbol == p.symbol.name
            and p.date >= start
            and p.date <= end
        )
        stock_data = [[i.close, i.open, i.low, i.high] for i in bars]
        df = pd.DataFrame(stock_data, columns=["Close", "Open", "Low", "High"])
        return df