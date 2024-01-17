import builtins
from dataclasses import dataclass
from backtesting import Backtest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pystockdb.db.schema.stocks import Stock, Price
import pandas as pd
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.helper import my_now
import re


@dataclass
class BacktestResult:
    symbol: str
    strategy: str
    parameter: dict
    stats: pd.DataFrame

    def to_dict(self):
        # transform result to dict and skip all attributes starting with _
        filtered_dict = {
            k: v for k, v in self.stats.to_dict().items() if not k.startswith("_")
        }
        # remove all non-alpha characters from the key and replace % with _percent replace whitespace with _ and make all keys lowercase
        filtered_dict = {
            re.sub(
                r"[^a-zA-Z0-9_%]",
                "",
                k.replace("%", "percent").replace(" ", "_"),
            ).lower(): v
            for k, v in filtered_dict.items()
        }

        return {
            "symbol": self.symbol,
            "strategy": self.stats["_strategy"].name,
            "parameter": self.stats["_strategy"].get_parameters(),
            "stats": filtered_dict,
        }


class StartBase:
    def __init__(self, ticker_symbols: list[str], strategies: list[BaseStrategy], parameters: list[dict]):
        self.strategies: list[BaseStrategy] = strategies
        self.parameters: list[dict] = parameters
        self.ticker_symbols: list[str] = ticker_symbols

    def run_implementation(
        self, strategy: BaseStrategy, symbol: str, df: pd.DataFrame, commission: float, parameter: dict
    ) -> BacktestResult:
        raise NotImplementedError()

    def run(self, commission=0.002, history_months=6) -> list[BacktestResult]:
        if self.parameters and len(self.strategies) != len(self.parameters):
            raise RuntimeError()
        backtest_results: list[BacktestResult] = []
        for idx, strategy in enumerate(self.strategies):
            for symbol in self.ticker_symbols:
                parameter = None
                if self.parameters:
                    parameter = self.parameters[idx]
                now = my_now()
                before = now + relativedelta(months=-history_months)
                bars = Price.select(
                    lambda p: symbol == p.symbol.name
                    and p.date >= before
                    and p.date <= now
                )
                stock_data = [[i.close, i.open, i.low, i.high] for i in bars]
                df = pd.DataFrame(stock_data, columns=["Close", "Open", "Low", "High"])
                backtest_results.append(
                    self.run_implementation(strategy, symbol, df, commission, parameter)
                )
        return backtest_results
