from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy.bollinger_volume_strategy import BollingerVolumeStrategy
from pystockfilter.tool.start_backtest import StartBacktest

BollingerVolumeStrategy.caching = False
strategies = [BollingerVolumeStrategy]

# Define parameters for each strategy
parameters = [
    {
        "para_bb_window":14,  # Short Moving Average window
        "para_bb_std_dev": 1.2,  # Long Moving Average window
        "para_volume_window": 14,  # RSI window
        "para_volume_multiplier": 1.2,  # RSI threshold for trend confirmation
    },
]  

# Initialize backtest with data source
backtest = StartBacktest(
    ["AAPL"],
    strategies,
    parameters,
    data_source=Data(Data.Y_FINANCE_CACHE),
)

results = backtest.run(commission=0.001, cash=10000000, history_months=6)

# Print and plot results
for result in results:
    result.bt.plot(open_browser=True) 
    print(f"Strategy: {result.strategy} - {result.symbol} | Profit: {result.earnings} | Status: {result.status}")
