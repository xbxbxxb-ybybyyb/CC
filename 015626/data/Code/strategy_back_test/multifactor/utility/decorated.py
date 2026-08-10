import datetime as dt
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import pandas as pd
import numpy as np


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


@static_vars(tic=dt.datetime.now())
def pprint(*args, **kwargs):
    print(('%.3fs <- prev msg: ' % (dt.datetime.now() - pprint.tic).total_seconds()).rjust(22), *args, **kwargs)
    pprint.tic = dt.datetime.now()


@static_vars(tic=dt.datetime.now())
def tprint(*args, **kwargs):
    print(('%.3fs elapsed: ' % (dt.datetime.now() - tprint.tic).total_seconds()).rjust(18), *args, **kwargs)


@static_vars(cache=None)
def retrieve_st_stocks(date):
    date = IO.str_date_parser(date)
    if retrieve_st_stocks.cache is None:
        cache = IO.read_data(columns=['REMOVE_DT', 'ENTRY_DT'], dtable=DTable.AShareST).reset_index('dt', drop=True)
        cache['REMOVE_DT'] = pd.to_datetime(cache['REMOVE_DT'], format='%Y%m%d')
        cache['ENTRY_DT'] = pd.to_datetime(cache['ENTRY_DT'], format='%Y%m%d')
        cache['REMOVE_DT'].loc[cache['REMOVE_DT'].isnull()] = pd.Timestamp.max
        retrieve_st_stocks.cache = cache
    else:
        cache = retrieve_st_stocks.cache
    return cache[(cache['ENTRY_DT'] <= date) & (cache['REMOVE_DT'] > date)].index.unique().tolist()


@static_vars(cache=dict())
def cached_read_data(dates, **kwargs):
    assert len(dates) == 2
    start_date = IO.str_date_parser(dates[0])
    end_date = IO.str_date_parser(dates[1])
    key = tuple(kwargs.values())
    if key in cached_read_data.cache:
        data = cached_read_data.cache[key]
    else:
        data = IO.read_data(**kwargs)
        cached_read_data.cache[key] = data
    return data.loc[start_date:end_date]

