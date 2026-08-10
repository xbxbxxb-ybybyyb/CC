from xquant.factordata import FactorData
s = FactorData()

import datetime
import pandas as pd
import os, pickle
import numpy as np
from arrow.naming_config import *
from arrow.link_v2 import LinkMessage
import functools
import dill
import re
import bottleneck as bk
import json
import sched, time
import logging
import sys
from arrow import xquant_data

from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from multifactor.data.utils import *


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(cache=None)
def retrieve_st_stocks(date):
    date = IO.str_date_parser(date)
    if retrieve_st_stocks.cache is None:
        cache = IO.read_data(columns=['REMOVE_DT', 'ENTRY_DT', 'S_TYPE_ST'], dtable=DTable.AShareST).reset_index('dt', drop=True)
        cache = cache.loc[cache['S_TYPE_ST'] != 'R']
        cache['REMOVE_DT'] = pd.to_datetime(cache['REMOVE_DT'], format='%Y%m%d')
        cache['ENTRY_DT'] = pd.to_datetime(cache['ENTRY_DT'], format='%Y%m%d')
        cache['REMOVE_DT'].loc[cache['REMOVE_DT'].isnull()] = pd.Timestamp.max
        retrieve_st_stocks.cache = cache
    else:
        cache = retrieve_st_stocks.cache
    return cache[(cache['ENTRY_DT'] <= date) & (cache['REMOVE_DT'] > date)].index.unique().tolist()
    
def get_universe(today):
    print(f'update universe {today}')
    dates = s.tradingday((pd.Timestamp(today) - datetime.timedelta(days = 60)).strftime('%Y%m%d'), today)

    date_bgn = dates[0]
    date_end = dates[-2]

    data = IO.read_data([date_bgn, date_end], alt = '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5')
    filt = IO.read_data([date_bgn, date_end], dtype=DType.STOCK, ftype=FType.UNIV, dsource=DSource.OPTM)
    data = data.join(filt)
    data.Listing_date = data.Listing_date.groupby('Ticker').fillna(method = 'ffill').fillna(0).astype('int')

    data = data[data.Listing_date > 0]

    data['listing_days'] = [x.days for x in np.array([x[0] for x in data.index]) - np.array([pd.Timestamp(str(x)) for x in data.Listing_date.values])]
    data['filter_subnew'] = ((data.listing_days > 1) & (data.S_DQ_LOW < data.S_DQ_LIMIT)).groupby('Ticker').expanding().sum().reset_index(level = 0, drop = True) > 1
    data['filter_SHSZ'] = data.reset_index()['Ticker'].str.contains('SH|SZ').values


    data['filter_1'] = (data.S_DQ_HIGH == data.S_DQ_LIMIT) & (data.S_DQ_CLOSE < data.S_DQ_LIMIT)

    data['filter_2'] = (data.S_DQ_HIGH > 1.04 * data.S_DQ_OPEN) & (data.S_DQ_CLOSE < data.S_DQ_OPEN)

    data['filter_3'] = (data.groupby('Ticker').shift(1).S_DQ_CLOSE == data.groupby('Ticker').shift(1).S_DQ_LIMIT) & (data.S_DQ_CLOSE < data.S_DQ_LIMIT)

    data['filter_4'] = data.S_DQ_CLOSE > data.S_DQ_STOPPING

    daily_universe = data[data.filter_subnew & \
                          data.filter_SHSZ & \
                          data.filter_4 & \
                          (data.filter_1 | data.filter_2 | data.filter_3)]

    ##############次新股加入blacklist##############
    daily_universe = daily_universe.loc[pd.Timestamp(date_end)]

    daily_universe = list(daily_universe.reset_index()['Ticker'])
    st_stocks = retrieve_st_stocks(today)
    stocklist = [x for x in daily_universe if x not in st_stocks]

    stocklist = pd.DataFrame({'dt':[pd.Timestamp(today)] * len(stocklist), 'Ticker':stocklist}).set_index(['dt', 'Ticker'])
    stocklist = stocklist.join(data.loc[pd.Timestamp(date_end)][['filter_1', 'filter_2', 'filter_3']])

    return stocklist


def update_universe() :
    print('start update universe')
    # universe_path = '/dfs/group/800466/warehouse/Arrow/arrow_prod/universe/arrow_universe.pkl'
    univ = pd.read_pickle(universe_path)

    univ_lastdate = univ.index.get_level_values(0)[-1].strftime('%Y%m%d')

    now_tradingday,_,_ = check_update_date()

    next_tradingday = udt.get_trading_day_offset(now_tradingday, 1)[0].strftime('%Y%m%d')
    next_dataday = udt.get_trading_day_offset(univ_lastdate, 1)[0].strftime('%Y%m%d')

    if next_tradingday == univ_lastdate:
        print('universe already update to date')
        return

    date_list = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(next_dataday, next_tradingday)]

    all_univ_list = [univ]
    for date in date_list:
        _univ = get_universe(date)
        all_univ_list.append(_univ)

    all_univ = pd.concat(all_univ_list, axis = 0)
    all_univ = all_univ[~all_univ.index.duplicated()].sort_index()

    all_univ.to_pickle(universe_path)
    print('update universe done')

def update_level2_data_for_universe(date, download_t_1_data = False, download_t_data = False, force_override = False, kind = 'history'):
    
    univ = pd.read_pickle(universe_path)
    _univ = univ.loc[str(date)]
    if download_t_1_data:
        print(f'start download {date} t-1 level2 data')
        univ_dt = _univ.index.get_level_values(0)[0]
        univ_preday_dt = udt.get_trading_day_offset(univ_dt, -1)[0]
        _univ_preday = pd.DataFrame({'dt':[univ_preday_dt] * len(_univ), 'Ticker':_univ.reset_index().Ticker}).set_index(['dt','Ticker'])

        xquant_data.retrieve_level2_by_h5(_univ_preday, data_root, 'Stock', 24, force_override = force_override)
        xquant_data.retrieve_level2_by_h5(_univ_preday, data_root, 'Transaction', 24, force_override = force_override)
        xquant_data.retrieve_level2_by_h5(_univ_preday, data_root, 'Order', 24, force_override = force_override)
        xquant_data.retrieve_level2_by_h5(_univ_preday, data_root, 'Order_RAW', 24, force_override = force_override)
        print(f'end download {date} t-1 level2 data')

    if download_t_data:
        save_path = hot_data_root if kind == 'history' else today_data_root
        print(f'start download {date} t level2 data')
        xquant_data.retrieve_level2_by_h5(_univ, save_path, 'Stock', 24, force_override = force_override)
        xquant_data.retrieve_level2_by_h5(_univ, save_path, 'Transaction', 24, force_override = force_override)
        xquant_data.retrieve_level2_by_h5(_univ, save_path, 'Order', 24, force_override = force_override)
        xquant_data.retrieve_level2_by_h5(_univ, save_path, 'Order_RAW', 24, force_override = force_override)
        print(f'end download {date} t level2 data')


    
