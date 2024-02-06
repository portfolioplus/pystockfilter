
from backtesting import Backtest
import pandas as pd
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.tool.chunked_optimizer import ChunkedOptimizer
from pystockfilter.tool.start_base import BacktestResult, StartBase


class StartChunkedOptimizer(StartBase):

    def __init__(self, ticker_symbols: list[str], strategies: list[BaseStrategy], optimizer_parameters: list[dict], chunk_size=100, num_processes=4):

        super().__init__(ticker_symbols, strategies, optimizer_parameters)
        self.chunk_size = chunk_size
        self.num_processes = num_processes


    def run_implementation(self, strategy: BaseStrategy, symbol: str, df: pd.DataFrame, commission: float, parameter: dict) -> BacktestResult:
        bt = ChunkedOptimizer(strategy, parameter, df, commission=commission, chunk_size=self.chunk_size, num_processes=self.num_processes)
        result = bt.optimize()
        return BacktestResult(
            symbol=symbol,
            strategy=result["_strategy"].name,
            parameter=result["_strategy"].get_parameters(),
            stats=result,
        )