from copy import copy
import os
import json
import pytest
import pandas as pd
from pystockfilter.strategy.base_strategy import Signals
from pystockfilter.strategy.rsi_strategy import RSIStrategy
from pystockfilter.tool.result import BacktestResult, BacktestResultList


@pytest.fixture()
def test_result(apple_data):
    symbol = "AAPL"
    parameter = {"param1": 10, "param2": 5}

    # Initializing strategy
    strategy = RSIStrategy(None, apple_data, {})
    strategy.init()

    # Creating a mock stats series
    s = pd.Series(dtype=object)
    s["Avg. Trade [%]"] = 2.35371
    s["Profit Factor"] = 2.35371
    s["Expectancy [%]"] = 8.35371
    s["Return [%]"] = 2.916893
    s["_strategy"] = strategy
    s["SQN"] = 2.916893

    # Mock BacktestResult
    backtest_result = BacktestResult(
        symbol=symbol,
        strategy=strategy.name,
        parameter=parameter,
        stats=s,
        status=Signals.BUY,
        bt=None,
        earnings=5.0,
        sqn=2.0,
        time_taken=1.0,
    )
    return backtest_result


@pytest.fixture()
def result_list(test_result):
    """Fixture that returns a BacktestResultList with one item"""
    return BacktestResultList([test_result])


def test_greater_than_same(test_result):
    """Test greater than operation with equal objects"""
    other_result = test_result
    assert (test_result > other_result) == False, "Results should be equal"


def test_greater_than_diff_sqn(test_result):
    """Test greater than with different SQN values"""
    other_result = test_result
    other_result.sqn = 3.0  # Modify SQN
    assert (test_result > other_result) == False, "Test result should have lower SQN"


def test_addition(test_result):
    """Test addition operation for BacktestResult"""
    other_result = test_result
    result = test_result + other_result

    assert result.earnings == 10.0, "Earnings should sum up"
    assert result.time_taken == 2.0, "Time taken should sum up"
    assert result.sqn == 4.0, "SQN should sum up"


def test_to_dict(test_result):
    """Test conversion to dictionary format"""
    result_dict = test_result.to_dict()

    assert result_dict["symbol"] == "AAPL"
    assert result_dict["earnings"] == 2.916893
    assert "stats" in result_dict
    assert isinstance(result_dict["stats"], dict), "Stats should be a dictionary"


def test_to_dict_optimization(test_result):
    """Test dictionary conversion for optimization"""
    opt_dict = test_result.to_dict_optimization()

    assert opt_dict["strategy"] == "RSIStrategy", "Strategy should be a string"
    assert opt_dict["earnings"] == 5.0, "Earnings should match expected"
    assert "calculation_time" in opt_dict, "Should include calculation time"


def test_invalid_comparison(test_result):
    """Test invalid comparison between BacktestResult and non-compatible type"""
    with pytest.raises(TypeError):
        _ = test_result > 5  # Invalid comparison


def test_dump_optimization_results(tmp_path, result_list):
    """Test dumping optimization results to a file without appending"""
    file_path = os.path.join(tmp_path, "optimization_results.json")

    # Ensure no file exists initially
    assert not os.path.exists(file_path), "File should not exist before dumping"

    # Dump results to file
    result_list.dump_optimization_results(file_path)

    # Verify file exists
    assert os.path.exists(file_path), "File should exist after dumping"

    # Read the file and verify content
    with open(file_path, "r") as f:
        data = json.load(f)

    assert "AAPL" in data, "Symbol key (AAPL) should be in the dumped data"
    assert (
        len(data["AAPL"]) == 1
    ), "There should be one result under the AAPL symbol key"
    assert (
        data["AAPL"]["RSIStrategy"]["earnings"] == 5.0
    ), "Earnings should match the expected value"


def test_dump_optimization_results_append(tmp_path, result_list, test_result):
    """Test dumping optimization results with append mode"""
    file_path = os.path.join(tmp_path, "optimization_results_append.json")

    # Dump initial results
    result_list.dump_optimization_results(file_path)
    result_cpy = copy(result_list[0])
    result_cpy.strategy = "SmaCrossCloseStrategy"
    # Append more results to the list
    result_list.append(result_cpy)
    result_list.dump_optimization_results(file_path, append=True)

    # Read and verify the appended content
    with open(file_path, "r") as f:
        data = json.load(f)

    assert "AAPL" in data, "Symbol key (AAPL) should be in the dumped data"
    assert (
        len(data["AAPL"]) == 2
    ), "There should be two results under the AAPL symbol key"
    assert (
        data["AAPL"]["RSIStrategy"]["earnings"] == 5.0
    ), "Second earnings should match the expected value"


def test_pretty_print_option(tmp_path, result_list):
    """Test pretty print option in dump_optimization_results"""
    file_path = os.path.join(tmp_path, "optimization_pretty_print.json")

    # Dump results with pretty print
    result_list.dump_optimization_results(file_path, pretty_print=True)

    # Read the file and verify the formatting (with indentation)
    with open(file_path, "r") as f:
        content = f.read()

    assert content.startswith(
        "{\n"
    ), "File should be pretty-printed with new lines and indentation"

    # Now dump without pretty print
    result_list.dump_optimization_results(file_path, pretty_print=False)

    with open(file_path, "r") as f:
        content = f.read()

    assert not content.startswith(
        "{\n"
    ), "File should not be pretty-printed (no new lines or indentation)"
