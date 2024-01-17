# Example: Optimizing Parameters for EmaCrossEmaStrategy using Chunked Optimizer
# Why use chunking? Chunking allows the optimizer to break down historical data into manageable chunks, 
# optimizing each one separately. This helps prevent overfitting to specific, potentially anomalous events 
# and promotes a strategy that is more robust across varied data patterns, improving its future performance.

import multiprocessing as mp
from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy.ema_cross_ema_strategy import EmaCrossEmaStrategy
from pystockfilter.tool.start_chunked_optimizer import StartChunkedOptimizer
from pystockfilter.tool.start_optimizer import StartOptimizer


# Set multiprocessing method to enhance optimization speed
mp.set_start_method("fork")

# Define the trading strategy and the parameters to optimize
strategies = [EmaCrossEmaStrategy]

# Set up parameter ranges for optimization, ensuring logical constraints
parameters = [
    {
        "para_ema_short":  range(2, 60),               # Short EMA range for optimization
        "para_ema_long": range(20, 150),                # Long EMA range for optimization
        "constraint": lambda p: p.para_ema_long > p.para_ema_short 
                              and (p.para_ema_long - p.para_ema_short) > 7,
        "maximize": "Equity Final [$]",                # Target final equity as the optimization goal
    }
]

# Initialize the chunked optimizer with specific stock data, strategy, and parameters
optimizer = StartChunkedOptimizer(
    ticker_symbols=["AAPL"],
    strategies=strategies,
    optimizer_parameters=parameters,
    optimizer_class=StartOptimizer,
    data_source=Data(Data.Y_FINANCE),
    data_chunk_size=300, # size of each data chunk
)

# Execute the optimization process over the past 24 months of historical data
results = optimizer.run(history_months=24)
best_result = results[0]

# Output the optimized parameters and results
print(
    f"Optimal Result: Final equity of {best_result.earnings} achieved with parameters {best_result.parameter}, "
    f"using strategy {best_result.strategy}. Process completed in {best_result.time_taken}."
)
