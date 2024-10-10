from pystockfilter.data import StockDataSource
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.start_base import StartBase


class StartBacktest(StartBase):

    def __init__(self, ticker_symbols: list[str], strategies: list[BaseStrategy], parameters: list[dict], data_source: StockDataSource):
        super().__init__(ticker_symbols, strategies, parameters, data_source)
