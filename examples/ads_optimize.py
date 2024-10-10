# Example: Optimizing Parameters for EmaCrossEmaStrategy using Optimizer Class

import multiprocessing as mp
from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy.ema_cross_ema_strategy import EmaCrossEmaStrategy
from pystockfilter.tool.start_optimizer import StartOptimizer

# Set multiprocessing method to enhance optimization speed
mp.set_start_method("fork")

# Define the trading algorithm and the parameters to optimize
strategies = [EmaCrossEmaStrategy]

# Define parameter ranges for optimization, with constraints for logical values
parameters = [
    {
        "para_ema_short": range(2, 50),               # Short EMA range to optimize
        "para_ema_long": range(10, 150),              # Long EMA range to optimize
        "constraint": lambda p: p.para_ema_long > p.para_ema_short 
                              and (p.para_ema_long - p.para_ema_short) > 7,
                       # Optimize for final equity value
    }
]

# Initialize optimizer with specified stock, strategy, parameters, and data source
optimizer = StartOptimizer(
    tickers=["ADS.F"],
    strategies=strategies,
    parameters=parameters,
    data_source=Data(Data.Y_FINANCE_CACHE),
)

# Run the optimizer over 24 months of historical data
results = optimizer.run(history_months=24)
best_result = results[0]

# Print the optimized parameters and results
print(
    f"Optimal result: {best_result.earnings} with parameters {best_result.parameter}, "
    f"strategy: {best_result.strategy}, time taken: {best_result.time_taken}"
)
