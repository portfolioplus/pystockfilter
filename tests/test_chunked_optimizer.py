
import pytest
from pystockfilter.tool.start_chunked_optimizer import StartChunkedOptimizer
from pystockfilter.tool.start_optimizer import StartOptimizer
import pystockfilter.tool.start_seq_optimizer as start_seq_optimizer
from pystockfilter.data.stock_data_source import DataSourceModule as Data
from pystockfilter.strategy.rsi_strategy import RSIStrategy as rsi



def test_validate_raises_error_for_invalid_parameter():
    
    # Define invalid parameters (para_test < chunk_size)
    invalid_optimizer_arg = [
        {"para_test": 50, "other_param": 200},  # para_test < chunk_size
        {"para_enter": 30, "para_exit": 40}    # Should not be checked due to "enter" and "exit" in name
    ]
    
    # Initialize optimizer with invalid parameters
    optimizer = StartChunkedOptimizer(
        strategies=[rsi],
        ticker_symbols=["TEST"],
        optimizer_parameters=invalid_optimizer_arg,
        data_source=Data(source=Data.LOCAL, options={"STOCK_DATA_PATH": "tests/test_data"}),
        data_chunk_size=10,
        optimizer_class=StartOptimizer
    )

    # Assert that ValueError is raised with the expected message
    with pytest.raises(ValueError, match="para_test must be lower than data chunk size"):
        optimizer.validate()

def test_validate_passes_for_valid_parameters():
    # Define valid parameters (all para_ > chunk_size or contain "enter" or "exit")
    valid_optimizer_arg = [
        {"para_test": 1, "para_another": 2},
        {"para_enter": 30, "para_exit": 40}
    ]
    
    # Initialize optimizer with valid parameters
    optimizer = StartChunkedOptimizer(
        strategies=[rsi],
        ticker_symbols=["TEST"],
        optimizer_parameters=valid_optimizer_arg,
        data_source=Data(source=Data.LOCAL, options={"STOCK_DATA_PATH": "tests/test_data"}),
        data_chunk_size=10,
        optimizer_class=StartOptimizer
    )

    # Validate should pass without raising an error
    optimizer.validate()

def test_chunked_sequential_optimizer():
    opt = StartChunkedOptimizer(
        ["AAPL"],
        [rsi],
        [
            [
                {
                    "para_rsi_window": range(14, 16, 1),
                    
                },
                {
                    "para_rsi_enter": range(65, 70, 1),
                    "para_rsi_exit": range(20, 30, 1),
                    "constraint": lambda p: p.para_rsi_enter > p.para_rsi_exit
                    and p.para_rsi_enter - p.para_rsi_exit > 10,
                    
                },
            ],
        ],
        start_seq_optimizer.StartSequentialOptimizer,
        Data(source=Data.LOCAL, options={"STOCK_DATA_PATH": "tests/test_data"}),
    )
    result = opt.run(history_months=160)
    assert len(result) == 1