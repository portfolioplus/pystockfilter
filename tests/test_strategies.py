from datetime import datetime
from math import nan
from unittest.mock import patch

import pandas as pd
import pytest
from pandas import testing as tm

import pystockfilter.strategy as st
from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy import StrategyName, strategy_from_name
from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy
from pystockfilter.strategy.rsi_strategy import RSIStrategy
from pystockfilter.strategy.sma_cross_sma_strategy import SmaCrossSmaStrategy
from pystockfilter.strategy.uo_strategy import UltimateStrategy
from pystockfilter.tool.start_backtest import StartBacktest
from pystockfilter.tool.start_chunked_optimizer import StartChunkedOptimizer
from pystockfilter.tool.start_optimizer import StartOptimizer
from pystockfilter.tool.start_seq_optimizer import StartSequentialOptimizer

INPUT_CLOSE = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], name="Close")

ECCS = strategy_from_name(StrategyName.ECCS)
ECES = strategy_from_name(StrategyName.ECES)
ECSS = strategy_from_name(StrategyName.ECSS)
SCSS = strategy_from_name(StrategyName.SCSS)
SCCS = strategy_from_name(StrategyName.SCCS)
RSIS = strategy_from_name(StrategyName.RSIS)
UO = strategy_from_name(StrategyName.UO)
UECCS = strategy_from_name(StrategyName.UECCS)
UECES = strategy_from_name(StrategyName.UECES)
DOJI_RSI = strategy_from_name(StrategyName.DOJI_RSI)

def strategy_setup(data, parameters, strategy_class):
    strategy = strategy_class(None, data, parameters)
    strategy.init()
    return strategy


# Parameterized test for strategy initialization
@pytest.mark.parametrize(
    "strategy_class, parameters",
    [
        (ECCS, {"para_ema_short": 14}),
        (ECES, {"para_ema_short": 14, "para_ema_long": 50}),
        (ECSS, {"para_ema_short": 14, "para_sma_short": 50}),
        (SCSS, {"para_sma_short": 14, "para_sma_long": 50}),
        (SCCS, {"para_sma_short": 14}),
        (
            RSIS,
            {"para_rsi_window": 3, "para_rsi_enter": 5, "para_rsi_exit": 22},
        ),
        (
            UO,
            {
                "para_uo_short": 7,
                "para_uo_medium": 14,
                "para_uo_long": 28,
                "para_uo_upper": 70,
                "para_uo_lower": 30,
            },
        ),
        (
            UECCS,
            {
                "para_uo_short": 6,
                "para_uo_medium": 13,
                "para_uo_long": 27,
                "para_uo_upper": 50,
                "para_uo_lower": 20,
                "para_ema_short": 7,
            },
        ),
        (
            UECES,
            {
                "para_uo_short": 5,
                "para_uo_medium": 12,
                "para_uo_long": 26,
                "para_uo_upper": 40,
                "para_uo_lower": 10,
                "para_ema_short": 5,
                "para_ema_long": 17,
            },
        ),
        (
            DOJI_RSI,
            {"para_rsi_period": 14, "para_confirmation_threshold": 3},
        )
        # Add other strategies and parameters here
    ],
)
def test_strategy_init(strategy_class, parameters, apple_data):
    strategy = strategy_setup(apple_data, parameters, strategy_class)
    attr_result = all(hasattr(strategy, attr) for attr in parameters.keys())
    attr_result_value = all(
        getattr(strategy, attr) == value for attr, value in parameters.items()
    )
    assert attr_result, f"Expected {parameters} but got {strategy.__dict__}"
    assert attr_result_value, f"Expected {parameters} but got {strategy.__dict__}"
    assert strategy.close is not None, "Close attribute is missing"
    assert strategy.sell_signal is not None, "Sell signal attribute is missing"
    assert strategy.buy_signal is not None, "Buy signal attribute is missing"


# Parameterized test for algo function
@pytest.mark.parametrize(
    "name, algo_func, parameters, data, expected_ema",
    [
        (
            "EmaCrossCloseStrategy",
            EmaCrossCloseStrategy.algo,
            {"para_ema_short": 2},
            INPUT_CLOSE,
            pd.Series([nan, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5], name="EMA_2"),
        ),
        (
            "SmaCrossSmaStrategy",
            SmaCrossSmaStrategy.algo,
            {"para_sma_short": 3},
            INPUT_CLOSE,
            pd.Series([nan, nan, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0], name="SMA_3"),
        ),
        (
            "RSIStrategy",
            RSIStrategy.algo,
            {"para_rsi_window": 14},
            pd.Series(range(1, 20), name="Close"),
            pd.Series(
                [
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    100,
                    100,
                    100,
                    100,
                    100,
                ],
                name="RSI_14",
            ),
        ),
        (
            "UltimateStrategy",
            UltimateStrategy.algo,
            {"para_uo_short": 7, "para_uo_medium": 14, "para_uo_long": 28},
            pd.DataFrame(
                {
                    "Close": range(1, 30),
                    "High": range(1, 30),
                    "Low": range(1, 30),
                }
            ),
            pd.Series(
                [
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    nan,
                    100,
                    100,
                ],
                name="UO_7_14_28",
            ),
        ),
    ],
)
def test_algo_function(name, algo_func, parameters, data, expected_ema):
    _ = name
    val = algo_func(data, **parameters)
    tm.assert_series_equal(val, expected_ema)


# Parameterized backtest test
@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@pytest.mark.parametrize(
    "strategy_class, parameters, stock_symbol, expected_earnings",
    [
        (strategy_from_name(StrategyName.ECCS), {"para_ema_short": 14}, "AAPL", 26.97),
        (
            strategy_from_name(StrategyName.ECES),
            {"para_ema_short": 12, "para_ema_long": 20},
            "AAPL",
            -3.17,
        ),
        (
            strategy_from_name(StrategyName.ECSS),
            {"para_ema_short": 14, "para_sma_short": 50},
            "AAPL",
            3.02,
        ),
        (
            strategy_from_name(StrategyName.SCSS),
            {"para_sma_short": 14, "para_sma_long": 50},
            "AAPL",
            -0.104,
        ),
        (strategy_from_name(StrategyName.SCCS), {"para_sma_short": 14}, "AAPL", 20.81),
        (
            strategy_from_name(StrategyName.RSIS),
            {"para_rsi_window": 3, "para_rsi_enter": 5, "para_rsi_exit": 22},
            "AAPL",
            -9.06,
        ),(
            strategy_from_name(StrategyName.ATR),
            {"para_atr_window": 24, "para_atr_enter": 0.5, "para_atr_exit": 0.2},
            "AAPL",
            20.64,
        ),(
            strategy_from_name(StrategyName.MACD),
            {"para_macd_fast": 12, "para_macd_slow": 26, "para_macd_signal": 9},
            "AAPL",
            10.36,
        ),(  
            strategy_from_name(StrategyName.BVS),
            {"para_bb_window": 7, "para_bb_std_dev": 1.6, "para_volume_window": 7, "para_volume_multiplier": 1.01},
            "AAPL",
            -25.26,
        ),(  
            strategy_from_name(StrategyName.MARSI),
            {"para_ma_short": 7, "para_ma_long": 21, "para_rsi_window": 14, "para_rsi_threshold": 50},
            "AAPL",
            6.40,
        ),(
            strategy_from_name(StrategyName.DOJI_RSI),
            {"para_rsi_period": 14, "para_confirmation_threshold": 3},
            "AAPL",
            8.9
        )
        # Add more combinations of strategies and expected results here
    ],
)
def test_backtest(my_now, strategy_class, parameters, stock_symbol, expected_earnings):
    bt = StartBacktest(
        [stock_symbol],
        [strategy_class],
        [parameters],
        Data(source=Data.LOCAL, options={"STOCK_DATA_PATH": "tests/test_data"}),
    )
    result = bt.run()
    assert len(result) == 1
    assert result[0].symbol == stock_symbol
    assert expected_earnings == pytest.approx(result[0].earnings, 0.01)


# Parameterized optimizer test
@patch("pystockfilter.tool.start_base.my_now", return_value=datetime(2019, 7, 30))
@pytest.mark.parametrize(
    "strategy_class, parameters_range, stock_symbol, expected_optimal_param, expected_earnings",
    [
        (
            ECCS,
            {"para_ema_short": range(15, 20, 1)},
            "AAPL",
            {"para_ema_short": 19},
            41.62,
        ),
        (
            ECES,
            {
                **ECES.get_optimizer_parameters(),
                **{"para_ema_short": range(1, 20, 1), "para_ema_long": range(2, 50, 1)},
            },
            "AAPL",
            {"para_ema_short": 18, "para_ema_long": 47},
            5.25,
        ),
        (
            strategy_from_name(StrategyName.SCCS),
            {"para_sma_short": range(10, 40, 1)},
            "AAPL",
            {"para_sma_short": 21},
            41.62,
        ),
        (
            SCSS,
            {
                **SCSS.get_optimizer_parameters(),
                **{"para_sma_short": range(1, 20, 1), "para_sma_long": range(2, 50, 1)},
            },
            "AAPL",
            {"para_sma_short": 16, "para_sma_long": 48},
            6.31,
        ),
        # (
        #    UO,
        #    {
        #        **UO.get_optimizer_parameters(),
        #        **{
        #            "para_uo_short": range(14, 20, 1),
        #            "para_uo_medium": range(28, 30, 1),
        #            "para_uo_long": range(45, 50, 1),
        #        },
        #    },
        #    "AAPL",
        #    {"para_uo_short": 16, "para_uo_medium": 28, "para_uo_long": 49, 'para_uo_lower': -24, 'para_uo_upper': 22},
        #    10.5,
        # )
    ],
)
def test_optimizer(
    my_now,
    strategy_class,
    parameters_range,
    stock_symbol,
    expected_optimal_param,
    expected_earnings,
):
    opt = StartOptimizer(
        [stock_symbol],
        [strategy_class],
        [parameters_range],
        Data(source=Data.LOCAL, options={"STOCK_DATA_PATH": "tests/test_data"}),
    )
    result = opt.run()
    assert len(result) == 1
    assert result[0].parameter == expected_optimal_param
    assert expected_earnings == pytest.approx(result[0].earnings, 0.01)


# Parameterized chunked optimizer test
@pytest.mark.parametrize(
    "strategy_class, parameters_range, stock_symbol, expected_optimal_param, expected_earnings",
    [
        (
            ECCS,
            {"para_ema_short": range(15, 20, 1)},
            "AAPL",
            {"para_ema_short": 18},
            150.65,
        ),
        # Add more combinations of strategies and expected results here
    ],
)
def test_chunked_optimizer(
    strategy_class,
    parameters_range,
    stock_symbol,
    expected_optimal_param,
    expected_earnings,
):
    opt = StartChunkedOptimizer(
        [stock_symbol],
        [strategy_class],
        [parameters_range],
        StartOptimizer,
        Data(source=Data.LOCAL, options={"STOCK_DATA_PATH": "tests/test_data"}),
    )
    result = opt.run(history_months=160)
    assert len(result) == 1
    assert result[0].parameter == expected_optimal_param
    assert expected_earnings == pytest.approx(result[0].earnings, 0.01)
