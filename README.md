# pystockfilter

![Release Build](https://github.com/portfolioplus/pystockfilter/workflows/Release%20Build/badge.svg)
![CI Build](https://github.com/portfolioplus/pystockfilter/workflows/CI/badge.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pystockfilter?style=plastic)
[![Coverage Status](https://coveralls.io/repos/github/portfolioplus/pystockfilter/badge.svg?branch=master)](https://coveralls.io/github/portfolioplus/pystockfilter?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ac0c6fc68b74408c976007bd3db823f0)](https://www.codacy.com/gh/portfolioplus/pystockfilter/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=portfolioplus/pystockfilter&amp;utm_campaign=Badge_Grade)

Create your own fundamental or chart based stock filter. All you need is a database set up with [pystockdb](https://github.com/portfolioplus/pystockdb).

## built-in filters

### technical filters

- [x] [ADX](https://en.wikipedia.org/wiki/Average_directional_movement_index)
- [x] [RSI](https://en.wikipedia.org/wiki/Relative_strength_index)

## install

```shell
pip install pystockfilter
```

## quick start

Build internal filters:

```python
import logging
from pystockdb.db.schema.stocks import db


# connect to database
arguments = {'db_args': {
    'provider': 'sqlite',
    'filename': db_path_test,
    'create_db': False
    }
}
db.bind(**arguments["db_args"])
db.generate_mapping()

```


## issue tracker

[https://github.com/portfolioplus/pystockfilter/issuese](https://github.com/portfolioplus/pystockfilter/issues")
