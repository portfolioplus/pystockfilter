# pystockfilter

[![Build Status](https://travis-ci.org/portfolioplus/pystockfilter.svg?branch=master)](https://travis-ci.org/portfolioplus/pystockfilter)
[![Coverage Status](https://coveralls.io/repos/github/portfolioplus/pystockfilter/badge.svg?branch=master)](https://coveralls.io/github/portfolioplus/pystockfilter?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/07e6231a5a8c415a9f27736e02a286da)](https://www.codacy.com/app/SlashGordon/pystockfilter?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=portfolioplus/pystockfilter&amp;utm_campaign=Badge_Grade)

Database for stocks based on [pony.orm](https://github.com/ponyorm/pony).
This package provides an create, sync and update tool.

At the moment we are only support a few stocks.
If you want to have more, please contribute [pytickersymbols](https://github.com/portfolioplus/pytickersymbols).

## install

```shell
pip install pystockfilter
```

## quick start

In all samples we use sqlite but you are free to use other providers.
For more information's please read [Connecting to the Database](https://docs.ponyorm.org/database.html).

Install sqlite stock db:

```python
import logging
from pystockdb.tools.create import CreateAndFillDataBase

logger = logging.getLogger('test')
config = {
    'max_history': 1,
    'indices': ['DAX'],
    'currency': 'EUR',
    'db_args': {
        'provider': 'sqlite',
        'filename': 'demo.sqlite',
        'create_db': True
    },
}
create = CreateAndFillDataBase(config, logger)
create.build()
```

Update sqlite stock db:

```python
import logging
from pystockdb.tools.update import UpdateDataBaseStocks

logger = logging.getLogger('test')
config = {
    'symbols': ['ALL'],
    'prices': True,       # update prices
    'fundamentals': True, # update fundamental stock data
    'db_args': {
        'provider': 'sqlite',
        'filename': 'demo.sqlite',
        'create_db': False
    },
}
update = UpdateDataBaseStocks(config, logger)
update.build()
```

Sync sqlite stock db:

```python
import logging
from pystockdb.tools.sync import SyncDataBaseStocks

logger = logging.getLogger('test')
config = {
    'max_history': 1,
    'indices': ['CAC 40'], # add new index to existing database
    'currency': 'EUR',
    'db_args': {
        'provider': 'sqlite',
        'filename': 'demo.sqlite',
    },
}
sync = SyncDataBaseStocks(config, logger)
sync.build()
```

## issue tracker

[https://github.com/portfolioplus/pystockdb/issuese](https://github.com/portfolioplus/pystockdb/issues")
