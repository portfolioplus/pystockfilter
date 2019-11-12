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

## issue tracker

[https://github.com/portfolioplus/pystockfilter/issuese](https://github.com/portfolioplus/pystockfilter/issues")
