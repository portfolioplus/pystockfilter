from unittest.mock import patch
from pystockfilter.data.yfinance_source import YFinanceDataSource
import pandas as pd
from pandas.testing import assert_frame_equal

@patch('yfinance.download')
def test_get_stock_data(mock_download):
    mock_df = pd.DataFrame({
        'Date': ['2020-01-01', '2020-01-02', '2020-01-03'],
        'Open': [1, 2, 3],
        'High': [1, 2, 3],
        'Low': [1, 2, 3],
        'Close': [1, 2, 3],
        'Volume': [100, 200, 300],
        'Adj Close': [1, 2, 3]
    })
    mock_download.return_value = mock_df
    ds = YFinanceDataSource()
    result = ds.get_stock_data('AAPL', '2020-01-01', '2020-01-03')
    assert_frame_equal(result, mock_df)