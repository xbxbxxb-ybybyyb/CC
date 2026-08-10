import pandas as pd
import numpy as np
from pathlib import Path
import json


def multi_astype(pd_raw):
    y = pd_raw.reset_index()
    y.Ticker = y.Ticker.astype('category')
    y.set_index(['dt', 'Ticker'], append=False, inplace=True)
    y = y.sort_index(level=0)
    return y

def multi_astype_obj(pd_raw):
    y = pd_raw.reset_index()
    y.Ticker = y.Ticker.astype('object')
    y.set_index(['dt', 'Ticker'], append=False, inplace=True)
    y = y.sort_index(level=0)
    return y

def pd_unstack(pd_raw):
    if type(pd_raw) == pd.DataFrame:
        columns_lst = pd_raw.columns
    elif type(pd_raw) == pd.Series:
        columns_lst = []
    else:
        raise AssertionError
    if len(columns_lst) > 1:
        rtn = {}
        for item in columns_lst:
            rtn[item]= pd_raw[item].unstack()
    else:
        rtn = pd_raw.unstack()
    return rtn


def tracer(key):
    path = Path.home().joinpath('multifactor.json')
    counter = read_tracer(path)
    counter = auto_add(key, counter)
    set_tracer(path, counter)


def read_tracer(path):
    Path.touch(path)
    with open(path, 'r') as fin:
        try:
            counter = json.load(fin)
        except json.JSONDecodeError:
            counter = None
    return counter


def set_tracer(path, value):
    Path.touch(path)
    with open(path, 'w') as fout:
        json.dump(value, fout)


def auto_add(key, var):
    if var is None:
        var = dict()
    if key in var:
        var[key] += 1
    else:
        var[key] = 1
    return var
