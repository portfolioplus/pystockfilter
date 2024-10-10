# This example demonstrates how to find optimal MACD strategy parameters for the DAX index.
import multiprocessing as mp
from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy.macd_strategy import MACDStrategy
from pystockfilter.tool.start_backtest import StartBacktest
from pystockfilter.tool.start_batch_optimizer import StartBatchOptimizer
from pytickersymbols import PyTickerSymbols as pts
from pystockfilter import logger

# Activate multiprocessing for backtesting
mp.set_start_method("fork")

# Retrieve DAX symbols
symbols = pts()
dax_symbols = symbols.get_dax_frankfurt_yahoo_tickers()
# filter  DPW.F DPWN.F BNRN.F because of missing data
dax_symbols = [symbol for symbol in dax_symbols if symbol not in ["FMEA.F", "DPW.F", "DPWN.F", "BNRN.F"]]

# Define the strategy and initial parameters for backtesting
strategies = [MACDStrategy]
initial_params = [{'para_macd_fast': 8, 'para_macd_slow': 17, 'para_macd_signal': 5}]

# Run backtest without optimization
backtest = StartBacktest(
    dax_symbols,
    strategies,
    initial_params,
    data_source=Data(Data.Y_FINANCE_CACHE)  # Using cached data for faster backtests
)
results = backtest.run(commission=0.001, history_months=24)
avg_profit = sum(result.earnings for result in results) / len(results)
print(f"Average profit without optimization: {avg_profit:.2f}")

# Initialize batch optimizer for parameter optimization
batch_optimizer = StartBatchOptimizer(
    dax_symbols,
    strategies,
    [MACDStrategy.get_optimizer_parameters()],
    data_source=Data(Data.Y_FINANCE_CACHE)
)

# Run optimization to find the best parameters
opt_results = batch_optimizer.run(commission=0.001, history_months=24)
optimal_params = opt_results[-1].parameter  # Using last result as optimal

print(f"Optimal parameters found: {optimal_params}")

# Run backtest with optimized parameters
optimized_backtest = StartBacktest(
    dax_symbols,
    strategies,
    [optimal_params],
    data_source=Data(Data.Y_FINANCE_CACHE)
)
opt_results = optimized_backtest.run(commission=0.001, history_months=24)
opt_avg_profit = sum(result.earnings for result in opt_results) / len(opt_results)
print(f"Average profit with optimization: {opt_avg_profit:.2f}")
