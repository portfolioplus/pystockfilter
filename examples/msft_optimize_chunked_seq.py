# Example: Efficient Parameter Optimization with Chunked Sequential Optimizer 
# 
# Why use a sequential optimizer? As the number of parameters grows, the computational cost of optimization 
# increases exponentially. For strategies with multiple parameters, this can lead to prohibitively long processing times. 
# By splitting the parameters into groups and optimizing them sequentially, we significantly reduce computation time. 
# We first optimize the parameters in Group 1, then use those results to inform the optimization of Group 2, and so forth. 
# This way, each group's optimized parameters improve the subsequent stage of the strategy, ensuring efficient performance.

import multiprocessing as mp
from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy.uo_strategy import UltimateStrategy
from pystockfilter.tool.start_chunked_optimizer import StartChunkedOptimizer
from pystockfilter.tool.start_seq_optimizer import StartSequentialOptimizer

# Set multiprocessing method to "fork" for optimized parallel processing in Unix-based systems.
mp.set_start_method("fork")

# Define the trading strategy and the parameters to optimize
strategies = [UltimateStrategy]

# Define parameter groups for sequential optimization
parameters = [
    # Strategy 1: Ultimate Oscillator (UO) Strategy
    [
         # Group 1: UO Strategy parameters for uo algo  with constraints
        {
            "para_uo_short": range(7, 30, 1),
            "para_uo_medium": range(14, 40, 1),
            "para_uo_long": range(28, 80, 1),
            "constraint": lambda p: (
                p.para_uo_long > p.para_uo_medium > p.para_uo_short
            ) and (p.para_uo_long - p.para_uo_medium) > 5
              and (p.para_uo_medium - p.para_uo_short) > 3,
            "maximize": "Equity Final [$]",
        }, # Group 2: UO Strategy upper and lower threshold values with constraints
        {
            "para_uo_upper": range(20, 100, 1),
            "para_uo_lower": range(-30, 50, 1),
            "constraint": lambda p: (
                p.para_uo_upper > p.para_uo_lower
            ) and (p.para_uo_upper - p.para_uo_lower) > 10,
            "maximize": "Equity Final [$]",
        }
    ]
]

# Initialize the chunked sequential optimizer with stock data, strategy, and parameter configurations
optimizer = StartChunkedOptimizer(
    ticker_symbols=["MSFT"],
    strategies=strategies,
    optimizer_parameters=parameters,
    optimizer_class=StartSequentialOptimizer,
    data_source=Data(Data.Y_FINANCE),
    data_chunk_size=300,  # Each chunk will contain 300 data points
)

# Run the optimizer on 24 months of historical data, returning the best configuration for the strategy
results = optimizer.run(history_months=24)
best_result = results[0]

# Output the results, showing optimized parameters, strategy, and performance metrics
print(
    f"Optimal Result: Achieved a final equity of {best_result.earnings} with parameters {best_result.parameter}. "
    f"Strategy: {best_result.strategy}. Process completed in {best_result.time_taken} seconds."
)
