# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from pystockfilter.data import StockDataSource
from os import path
import pandas as pd

class LocalDataSource(StockDataSource):
    STOCK_DATA_PATH = None 
    @staticmethod
    def get_stock_data(symbol: str, start: str, end: str):
        if not path.exists(LocalDataSource.STOCK_DATA_PATH):
            raise FileNotFoundError("Stock data path does not exist")
        data_path = path.join(LocalDataSource.STOCK_DATA_PATH,f"{symbol.upper()}.csv")
        if not path.exists(data_path):
            raise FileNotFoundError("Stock data file does not exist")
        data = pd.read_csv(data_path)
        # Convert date to datetime
        data["Date"] = pd.to_datetime(data["Date"], utc=True)
        data.set_index("Date", inplace=True)
        start = pd.to_datetime(start).tz_localize('UTC')
        end = pd.to_datetime(end).tz_localize('UTC')
        # Filter data
        data = data[(data.index >= start) & (data.index <= end)]
        return data