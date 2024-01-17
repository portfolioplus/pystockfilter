# This example demonstrates how to backtest a DAX trading strategy using the Backtest class.
from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy.ema_cross_ema_strategy import EmaCrossEmaStrategy
from pystockfilter.strategy.uo_ema_cross_close_strategy import UltimateEmaCrossCloseStrategy
from pystockfilter.tool.start_backtest import StartBacktest
from pytickersymbols import PyTickerSymbols as pts

# Get list of DAX symbols
symbols = pts()
dax_symbols = symbols.get_dax_frankfurt_yahoo_tickers()
strategies = [EmaCrossEmaStrategy, UltimateEmaCrossCloseStrategy]

# Define parameters for each strategy
parameters = [
    {
        "para_ema_short": 7,
        "para_ema_long": 20,
    },
    {
        "para_uo_short": 7,
        "para_uo_medium": 14,
        "para_uo_long": 28,
        "para_ema_short": 12,
        "para_uo_upper": 20,
        "para_uo_lower": 0,
    },
]

# Initialize backtest with data source
backtest = StartBacktest(
    dax_symbols,
    strategies,
    parameters,
    data_source=Data(Data.Y_FINANCE_CACHE),  # Use cached data source for faster backtests
    # In production, use Data.Y_FINANCE
)

results = backtest.run(commission=0.001, history_months=6)

# Print and plot results
for result in results:
    # result.bt.plot(open_browser=True)  # Uncomment to plot results in a browser
    print(f"Strategy: {result.strategy} - {result.symbol} | Profit: {result.earnings} | Status: {result.status}")
