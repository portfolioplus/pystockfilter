import pytest
from pystockfilter.data.local_source import LocalDataSource
import pandas as pd
from pandas.testing import assert_frame_equal
import os

@pytest.fixture
def test_data_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_data_path = os.path.join(base_dir, 'tests/test_data')
    return test_data_path

@pytest.fixture
def local_data_source(test_data_path):
    LocalDataSource.STOCK_DATA_PATH = test_data_path
    return LocalDataSource()

def test_get_stock_data(local_data_source, test_data_path):
    result = local_data_source.get_stock_data('AAPL', '2020-01-01', '2020-01-03')
    expected = pd.read_csv(os.path.join(test_data_path, 'AAPL.csv'))
    expected = expected[(expected.Date >= '2020-01-01') & (expected.Date <= '2020-01-03')]
    # index to datetime
    expected["Date"] = pd.to_datetime(expected["Date"], utc=True)
    expected.set_index("Date", inplace=True)
    assert_frame_equal(result, expected)

def test_get_stock_data_file_not_exist(local_data_source):
    with pytest.raises(FileNotFoundError):
        local_data_source.get_stock_data('XYZ', '2020-01-01', '2020-01-03')