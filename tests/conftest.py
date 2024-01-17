import os
from shutil import copyfile
from pystockdb.db.schema.stocks import db
import pytest
import pandas as pd


@pytest.fixture
def setup_test_database():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(test_dir, "testdb.sqlite")
    db_path_test = os.path.join(test_dir, "testdb_tmp.sqlite")
    if os.path.exists(db_path_test):
        os.remove(db_path_test)
    copyfile(db_path, db_path_test)
    arguments = {
        "db_args": {
            "provider": "sqlite",
            "filename": db_path_test,
            "create_db": False,
        }
    }
    if not db.provider:
        db.bind(**arguments["db_args"])
        db.generate_mapping()
    yield db


@pytest.fixture
def apple_data():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "test_data/AAPL.csv")
    data = pd.read_csv(path)
    return data


@pytest.fixture
def microsoft_data():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "test_data/MSFT.csv")
    data = pd.read_csv(path)
    return data


@pytest.fixture
def amazon_data():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "test_data/AMZN.csv")
    data = pd.read_csv(path)
    return data


@pytest.fixture
def google_data():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "test_data/GOOG.csv")
    data = pd.read_csv(path)
    return data
