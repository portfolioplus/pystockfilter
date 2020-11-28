# pystockfilter

[![Build Status](https://travis-ci.org/portfolioplus/pystockfilter.svg?branch=master)](https://travis-ci.org/portfolioplus/pystockfilter)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pystockfilter?style=plastic)
[![Coverage Status](https://coveralls.io/repos/github/portfolioplus/pystockfilter/badge.svg?branch=master)](https://coveralls.io/github/portfolioplus/pystockfilter?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/07e6231a5a8c415a9f27736e02a286da)](https://www.codacy.com/app/SlashGordon/pystockfilter?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=portfolioplus/pystockfilter&amp;utm_campaign=Badge_Grade)

Create your own fundamental or chart based stock filter. All you need is a database set up with [pystockdb](https://github.com/portfolioplus/pystockdb).

## built-in filters

### technical filters

- [x] [ADX](https://en.wikipedia.org/wiki/Average_directional_movement_index)
- [x] [RSI](https://en.wikipedia.org/wiki/Relative_strength_index)
- [x] StockIsHot: Simple trend indicator
- [x] StockIsHotSecure: improved StockIsHot version.

### fundamental filters

- [x] Lervermann
- [x] [Piotroski F-Score](https://en.wikipedia.org/wiki/Piotroski_F-Score)
- [x] Price Target Score: analysts price targets compared with actual price

## install

```shell
pip install pystockfilter
```

## quick start

Build internal filters:

```python
import logging
from pystockdb.db.schema.stocks import db

from pystockfilter.tool.build_internal_filters import BuildInternalFilters

# connect to database
arguments = {'db_args': {
    'provider': 'sqlite',
    'filename': db_path_test,
    'create_db': False
    }
}
db.bind(**arguments["db_args"])
db.generate_mapping()
# create internal filters for Adidas AG and Infineon
arguments = {'symbols': ['ADS.F', 'IFX.F']}
builder = BuildInternalFilters(arguments, logger)
builder.build()
# create internal filters for all stocks in database
arguments = {'symbols': ['ALL']}
builder = BuildInternalFilters(arguments, logger)
builder.build()
```

Build custom filters:

```python
import logging
import math
from datetime import datetime

import numpy as np
import tulipy as ti
import yfinance as yf
from dateutil.relativedelta import relativedelta
from pony.orm import db_session, select
from pystockdb.db.schema.stocks import Price, Tag
from pystockfilter.filter.base_filter import BaseFilter
from pystockfilter.base.base_helper import BaseHelper
from pystockfilter.tool.build_filters import BuildFilters

# custom filter 
class DividendKings(BaseFilter):
    """
    Calculates median of last dividends
    """

    NAME = 'DividendKings'

    def __init__(self, arguments: dict, logger: logging.Logger):
        self.buy = arguments['args']['threshold_buy']
        self.sell = arguments['args']['threshold_sell']
        self.lookback = arguments['args']['lookback']
        self.max_yield = arguments['args']['max_div_yield']
        super(DividendKings, self).__init__(arguments, logger)

    @db_session
    def analyse(self):
        symbol = select(sym.name for sym in self.stock.price_item.symbols
                        if Tag.YAO in sym.item.tags.name).first()
        try:
            yao_item = yf.Ticker(symbol)
            data = yao_item.dividends
        except ValueError:
            raise RuntimeError("Couldn't load dividends for {}".format(symbol))

        dates = data.index.array
        drop = []
        # let us calculate the dividend yield
        for my_date in dates:
            price = Price.select(
                    lambda p: p.symbol.name == symbol
                    and p.date.date() == my_date.date()
                ).first()
            if price:
                div_yield = (data[my_date] / price.close) * 100
                if div_yield > self.max_yield:
                    drop.append(my_date)
                    self.logger.error(
                        '{} has a non plausible div yield at {} ({} = {} / {} * 100).'
                        .format(symbol, my_date, div_yield, data[my_date], price.close)
                    )
                else:
                    data[my_date] = div_yield
            else:
                drop.append(my_date)
        data = data.drop(labels=drop)
        self.calc = data.median(axis=0)
        if self.calc is None or math.isnan(self.calc):
            raise RuntimeError("Couldn't calculate dividend yield.")
        return super(DividendKings, self).analyse()

    def get_calculation(self):
        return self.calc

    def look_back_date(self):
        return self.now_date + relativedelta(months=-self.lookback)

logger = BaseHelper.setup_logger("custom filter")

arguments_div = {
    "name": "DividendKings",
    "bars": False,
    "index_bars": False,
    "args": {
        "threshold_buy": 3,
        "threshold_sell": 0.2,
        "intervals": None,
        "max_div_yield": 9,
        "lookback": 2,
    },
}

symbols = ["ADS.F", "WDI.F", "BAYN.F"]

config_custom_filter = {
    "symbols": symbols,
    "filters": [DividendKings(arguments_div, logger)],
}

custom = BuildFilters(config_custom_filter, logger)
custom.build()
```

## issue tracker

[https://github.com/portfolioplus/pystockfilter/issuese](https://github.com/portfolioplus/pystockfilter/issues")
