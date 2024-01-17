


from pystockfilter.strategy.rsi_strategy import RSIStrategy
import pytest 

def test_rsi_strategy(apple_data):
    rsi = RSIStrategy(
        None,
        apple_data,
        {},
    )
    result = rsi.algo(apple_data['Close'], 14)
    result = rsi.algo(apple_data['Close'], 14)
    result = rsi.algo(apple_data['Close'], 14)
    assert rsi is not None


def test_rsi_strategy_cache(benchmark, apple_data):
    result = benchmark(RSIStrategy.algo, apple_data['Close'], 14)
    assert result is not None


@pytest.fixture
def rsi_strategy(apple_data):
    setattr(RSIStrategy, 'caching', True)
    return RSIStrategy(
        None,
        apple_data,
        {},
    )

@pytest.fixture
def rsi_strategy_no_cache(apple_data):
    setattr(RSIStrategy, 'caching', False)
    rsi = RSIStrategy(
        None,
        apple_data,
        {},
    )
    return rsi

def test_rsi_strategy_init(benchmark, rsi_strategy_no_cache):
    result = benchmark(rsi_strategy_no_cache.init)
    assert result is None

def test_rsi_strategy_init_cache(benchmark, rsi_strategy):
    result = benchmark(rsi_strategy.init)
    assert result is None