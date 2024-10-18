# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2024 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from datetime import datetime
from typing import Iterator


def float_range(start, stop, step) -> Iterator[float]:
    """
    Returns a range of float values
    :param start: start value
    :param stop: stop value
    :param step: step size
    :return: generator
    """
    while start < stop:
        yield float(start)
        start += float(step)


def float_range_list(start, stop, step) -> list[float]:
    """
    Returns a range of float values
    :param start: start value
    :param stop: stop value
    :param step: step size
    :return: generator
    """
    return list(float_range(start, stop, step))


def my_now():
    return datetime.now()
