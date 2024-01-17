# PyStockFilter

![Release Build](https://github.com/portfolioplus/pystockfilter/workflows/Release%20Build/badge.svg)
![CI Build](https://github.com/portfolioplus/pystockfilter/workflows/CI/badge.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pystockfilter?style=plastic)
[![Coverage Status](https://coveralls.io/repos/github/portfolioplus/pystockfilter/badge.svg?branch=master)](https://coveralls.io/github/portfolioplus/pystockfilter?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ac0c6fc68b74408c976007bd3db823f0)](https://www.codacy.com/gh/portfolioplus/pystockfilter/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=portfolioplus/pystockfilter&amp;utm_campaign=Badge_Grade)

PyStockFilter is a Python library that allows users to create custom stock filters using a range of fundamental and technical indicators. With support for data sources like Yahoo Finance, local data, and `pystockdb`, PyStockFilter is a versatile solution for building and backtesting technical and fundamental trading strategies.

## Features

- **Data Compatibility**: Integrates with Yahoo Finance, local data, and `pystockdb`.
- **Built-in Indicators**: Includes essential technical indicators, and supports custom indicator creation.
- **Backtesting**: Enables testing of strategies on historical data.
- **Optimization Tools**: Offers parameter optimization, including sequential and chunked data optimization.
- **Custom Strategy Support**: Extendable with your own strategies and indicators.

## Built-in Filters

### Technical Filters
PyStockFilter includes several popular technical indicators, which can be used out of the box or customized:

- **Simple Moving Average (SMA)**
- **Exponential Moving Average (EMA)**
- **Relative Strength Index (RSI)**
- **Ultimate Oscillator (UO)**

For custom indicators, refer to the examples in the `src/pystockfilter/strategy` directory.

## Installation

To install PyStockFilter, run:

```shell
pip install pystockfilter
```

## Quick Start Guide

For detailed examples on setting up strategies, defining parameters, and running the optimizer, please visit the [Examples Directory](https://github.com/portfolioplus/pystockfilter/tree/master/examples) in the PyStockFilter repository.

## Issue Tracker

Report issues, request features, or contribute via the GitHub Issue Tracker:

[PyStockFilter Issue Tracker](https://github.com/portfolioplus/pystockfilter/issues)
