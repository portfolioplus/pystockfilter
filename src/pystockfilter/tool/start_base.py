import builtins
from dataclasses import dataclass
from pystockfilter.backtesting import Backtest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pystockdb.db.schema.stocks import Stock, Price
import pandas as pd
from pystockfilter.data import StockDataSource
from pystockfilter.strategy.base_strategy import BaseStrategy, Signals
from pystockfilter.tool.helper import my_now
import re
from pystockfilter import logger

@dataclass
class BacktestResult:
    symbol: str
    strategy: str
    parameter: dict
    stats: pd.DataFrame
    status: Signals
    bt: Backtest
    earnings: float
    sqn: float = 0.0
    time_taken: float = 0.0

    def __gt__(self, other):
        if isinstance(other, BacktestResult):
            return self.sqn > other.sqn
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, BacktestResult):
            return BacktestResult(
                symbol=self.symbol,
                strategy=self.strategy,
                parameter=self.parameter,
                stats=self.stats,
                status=self.status,
                bt=self.bt,
                earnings=self.earnings + other.earnings,
                time_taken=self.time_taken + other.time_taken,
                sqn=self.sqn + other.sqn,
            )
        return NotImplemented
    
    @classmethod
    def from_stats_pd(cls, symbol: str, stats: pd.DataFrame, bt: Backtest, time_taken: float = 0.0):
        strategy:BaseStrategy = stats["_strategy"]
        return cls(
            symbol=symbol,
            strategy=strategy.name,
            parameter=strategy.get_parameters(),
            stats=stats,
            status=strategy.status(),
            bt=bt,
            earnings=stats["Return [%]"],
            time_taken=time_taken,
            sqn=stats["SQN"],
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            symbol=data["symbol"],
            strategy=data["strategy"],
            parameter=data["parameter"],
            stats=pd.DataFrame(data["stats"]),
            status=data["status"],
            bt=None,
            earnings=data["earnings"],
            time_taken=data["time_taken"],
            sqn=data["sqn"],
        )

    def to_dict(self):
        # transform result to dict and skip all attributes starting with _
        stats_dict = {
            k: v for k, v in self.stats.to_dict().items()
        }
        # remove all non-alpha characters from the key and replace % with _percent replace whitespace with _ and make all keys lowercase
        filtered_dict = {
            re.sub(
                r"[^a-zA-Z0-9_%]",
                "",
                k.replace("%", "percent").replace(" ", "_"),
            ).lower(): v
            for k, v in stats_dict.items()
            if not k.startswith("_")
        }
        filtered_dict["trades"] = stats_dict['_trades'].to_dict()
        return {
            "symbol": self.symbol,
            "status": self.stats["_strategy"].status(), 
            "strategy": self.stats["_strategy"].name,
            "parameter": self.stats["_strategy"].get_parameters(),
            "stats": filtered_dict,
            "earnings": self.stats["Return [%]"],
            "time_taken": self.time_taken, 
            "sqn": self.sqn    
        }


class StartBase:
    def __init__(self, ticker_symbols: list[str], strategies: list[BaseStrategy], parameters: list[dict], data_source: StockDataSource):
        self.strategies: list[BaseStrategy] = strategies
        self.parameters: list[dict] = parameters
        self.ticker_symbols: list[str] = ticker_symbols
        self.data_source = data_source
    
    def get_data(self, symbol: str, history_months: int) -> pd.DataFrame:
        now = my_now()
        before = now + relativedelta(months=-history_months)
        df = self.data_source.get_stock_data(symbol, before, now)
        return df

    def run(self, commission=0.002, cash=10000.0, history_months=6) -> list[BacktestResult]:
        if self.parameters and len(self.strategies) != len(self.parameters):
            raise RuntimeError()
        backtest_results: list[BacktestResult] = []
        for idx, strategy in enumerate(self.strategies):
            for symbol in self.ticker_symbols:
                logger.debug(f"Processing {symbol}")
                parameter = self.parameters[idx]
                df = self.get_data(symbol, history_months)
                # check if the dataframe is empty
                if df.empty:
                    logger.warning(f"Empty dataframe for {symbol}")
                    continue
                # add time measurement
                start_time = datetime.now()
                result = self.run_implementation(strategy, symbol, df, commission, cash, parameter)
                elapsed_time = datetime.now() - start_time
                if type(result) == tuple: # if the result is a tuple, we have an overall result and a last result
                    last_result, overall_result = result
                    backtest_results.append(last_result)
                    backtest_results.append(overall_result)
                else:
                    result.time_taken = elapsed_time.total_seconds()
                    backtest_results.append(
                        result
                    )
        return backtest_results

    def run_implementation(self, strategy: BaseStrategy, symbol: str, df: pd.DataFrame, commission: float, cash: float, parameter: dict) -> BacktestResult:
        strategy.set_parameters(strategy, parameter)
        start_time = datetime.now()
        bt = Backtest(df, strategy, commission=commission, cash=cash, trade_on_close=True, exclusive_orders=True)
        result = bt.run()
        time_taken = (datetime.now() - start_time).total_seconds()
        return BacktestResult.from_stats_pd(symbol, result, bt, time_taken)