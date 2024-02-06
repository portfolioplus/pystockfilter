import multiprocessing as mp
from backtesting import Backtest
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.strategy.uo_strategy import UltimateStrategy


class ChunkedOptimizer:
    def __init__(
        self,
        strategy: BaseStrategy,
        optimizer_arg: dict,
        data,
        chunk_size=100,
        num_processes=mp.cpu_count() - 1,
        cash=10000,
        commission=0.002,
        exclusive_orders=True,
        trade_on_close=True,
    ):
        self.data = data
        self.chunk_size = chunk_size
        self.num_processes = num_processes
        self.strategy: BaseStrategy = strategy
        self.optimizer_arg = optimizer_arg
        self.cash = cash
        self.commission = commission
        self.exclusive_orders = exclusive_orders
        self.trade_on_close = trade_on_close

    def _chunks(self, data):
        for i in range(0, len(data), self.chunk_size):
            yield (
                data[i : i + self.chunk_size],
                self.strategy,
                self.optimizer_arg,
                self.cash,
                self.commission,
                self.exclusive_orders,
                self.trade_on_close,
            )

    @staticmethod
    def _optimize_strategy(args):
        (
            chunk,
            strategy,
            optimizer_arg,
            cash,
            commission,
            exclusive_orders,
            trade_on_close,
        ) = args
        bt = Backtest(
            chunk,
            strategy,
            cash=cash,
            commission=commission,
            exclusive_orders=exclusive_orders,
            trade_on_close=trade_on_close,
        )
        stats = bt.optimize(**optimizer_arg)
        best_strategy = stats["_strategy"]
        best_params = best_strategy.get_parameters()
        return best_params

    def optimize(self) -> dict:
        best_stats = None

        pool = mp.Pool(self.num_processes)
        all_chunks = list(self._chunks(self.data))
        results = pool.map(self._optimize_strategy, all_chunks)
        pool.close()
        pool.join()
        # find best combination of parameters
        best_sub_final_equity = 0
        for best_param in results:
            self.strategy.set_parameters(self.strategy, best_param)
            bt = Backtest(
                self.data,
                self.strategy,
                cash=self.cash,
                commission=self.commission,
                exclusive_orders=self,
                trade_on_close=self.trade_on_close,
            )
            stats = bt.run()
            if stats["Equity Final [$]"] > best_sub_final_equity:
                best_sub_final_equity = stats["Equity Final [$]"]
                best_stats = stats

        best_stats["_strategy"] = self.strategy(None, None, best_param)
        return best_stats
