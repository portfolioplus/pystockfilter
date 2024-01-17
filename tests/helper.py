from pystockdb.db.schema.stocks import Index, Price
from pony.orm import db_session
from datetime import datetime
from dateutil.relativedelta import relativedelta


@db_session
def get_bars(symbol, my_filter):
    now = datetime.strptime("2019-07-30", "%Y-%m-%d")
    before = now + relativedelta(months=-my_filter.lookback)
    bars = Price.select(
        lambda p: p.symbol.name == symbol and p.date >= before and p.date <= now
    )
    return bars


@db_session
def get_index_bars(symbol, my_filter):
    now = datetime.strptime("2019-07-30", "%Y-%m-%d")
    before = now + relativedelta(months=-my_filter.lookback)
    my_index = Index.select(
        lambda i: symbol in i.stocks.price_item.symbols.name
    ).first()

    bars = Price.select(
        lambda p: p.symbol.name in my_index.price_item.symbols.name
        and p.date >= before
        and p.date <= now
    )
    return bars
