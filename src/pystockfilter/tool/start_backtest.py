
from backtesting import Backtest
import pandas as pd
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.start_base import BacktestResult, StartBase


class StartBacktest(StartBase):

    def __init__(self, ticker_symbols: list[str], strategies: list[BaseStrategy]):
        super().__init__(ticker_symbols, strategies, None)

    def run_implementation(self, strategy: BaseStrategy, symbol: str, df: pd.DataFrame, commission: float, parameter: dict) -> BacktestResult:
        bt = Backtest(df, strategy, commission=commission)
        result = bt.run()
        return BacktestResult(
            symbol=symbol,
            strategy=result["_strategy"].name,
            parameter=result["_strategy"].get_parameters(),
            stats=result,
        )
