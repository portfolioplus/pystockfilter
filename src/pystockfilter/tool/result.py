# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import json
from typing import List
from pystockfilter.backtesting import Backtest
import pandas as pd
from pystockfilter.strategy.base_strategy import BaseStrategy, Signals
import re
import os


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
    def from_stats_pd(
        cls, symbol: str, stats: pd.DataFrame, bt: Backtest, time_taken: float = 0.0
    ):
        strategy: BaseStrategy = stats["_strategy"]
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
        stats_dict = {k: v for k, v in self.stats.to_dict().items()}
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
        if "_trades" in self.stats:
            filtered_dict["trades"] = stats_dict["_trades"]
        return {
            "symbol": self.symbol,
            "status": self.stats["_strategy"].status(),
            "strategy": self.stats["_strategy"].name,
            "parameter": self.stats["_strategy"].get_parameters(),
            "stats": filtered_dict,
            "earnings": self.stats["Return [%]"],
            "time_taken": self.time_taken,
            "sqn": self.sqn,
        }

    def to_dict_optimization(self):
        return {
            "strategy": self.strategy,
            "parameter": self.parameter,
            "earnings": self.earnings,
            "sqn": self.sqn,
            "calculation_time": datetime.now().isoformat(),
        }


class BacktestResultList(List[BacktestResult]):

    def __add__(self, other):
        if isinstance(other, BacktestResultList):
            combined = BacktestResultList(self)
            combined.extend(other)
            return combined
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, BacktestResultList):
            return sum([result.earnings for result in self]) > sum(
                [result.earnings for result in other]
            )
        return NotImplemented

    def to_dict(self):
        return [result.to_dict() for result in self]

    @classmethod
    def from_dict(cls, data: List[dict]):
        return cls([BacktestResult.from_dict(result) for result in data])

    def dump_optimization_results(
        self, file_path: str, append=False, pretty_print=True
    ):
        result_dict = defaultdict(dict)
        if append and os.path.exists(file_path):
            with open(file_path, "r") as f:
                loaded_json = json.load(f)
                result_dict = defaultdict(dict, loaded_json)

        for result in self:
            res_dict = result.to_dict_optimization()
            strategy_key = res_dict.pop("strategy")
            result_dict[result.symbol][strategy_key] = res_dict

        with open(file_path, "w") as f:
            json.dump(result_dict, f, indent=4 if pretty_print else None)
