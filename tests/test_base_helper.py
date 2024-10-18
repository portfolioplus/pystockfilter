import numpy as np
from pystockfilter.base.base_helper import BaseHelper as bh
from pytest import approx

def test_convert_numpy_array():
    numpy_array = np.array([1, 2, 3])
    assert bh.convert_to_native(numpy_array) == [1, 2, 3]

def test_convert_numpy_scalar():
    numpy_scalar = np.float32(24.56)
    assert bh.convert_to_native(numpy_scalar) == approx(24.56)

def test_convert_nested_tuple():
    numpy_array = np.array([1, 2, 3])
    numpy_scalar = np.float32(24.56)
    numpy_tuple = (numpy_array, numpy_scalar, np.int32(7))
    native_tuple = bh.convert_to_native(numpy_tuple)
    assert native_tuple == ([1, 2, 3], approx(24.56), 7)

def test_convert_mixed_tuple():
    mixed_tuple = (np.float64(3.14), 42, "string", np.array([1, 2]), (np.float32(1.23), np.int64(9)))
    native_tuple = bh.convert_to_native(mixed_tuple)
    expected_tuple = (approx(3.14), 42, "string", [1, 2], (approx(1.23), 9))
    assert native_tuple == expected_tuple

def test_non_numpy_objects():
    assert bh.convert_to_native(42) == 42
    assert bh.convert_to_native("string") == "string"
    assert bh.convert_to_native([1, 2, 3]) == [1, 2, 3]
