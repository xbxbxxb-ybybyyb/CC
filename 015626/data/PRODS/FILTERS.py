import pandas as pd
import numpy as np
from shutil import copyfile
import os
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import pickle
from functools import partial
from joblib import Parallel, delayed
import datetime
import warnings
warnings.filterwarnings('ignore')
import bottleneck as bk
import datetime
from multifactor.data.utils import *
from datetime import timedelta
from multiprocessing.pool import Pool
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

import sys
sys.path.insert(4, '/data/user/016700/')
from operators_cc import *

universe = pd.read_hdf('/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')


for cat in ['IF.CFE', 'IC.CFE', 'IM.CFE']:
    print(cat)
    if ('IC' in cat) :
        multiplier = 200
        trail = ''
        siggg = pd.read_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear/minute_raw/amount_sum_30_if.h5').loc['20180101':]

    elif ('IM' in cat):
        multiplier = 200
        trail = '_im'
        siggg = pd.read_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear/minute_raw/amount_sum_30_if.h5').loc['20220722':]



    elif ('IF' in cat):
        multiplier = 300
        trail = '_if'
        siggg = pd.read_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear/minute_raw/amount_sum_30_if.h5').loc['20180101':]


    holder = pd.DataFrame()
    ic_universe = universe.xs(cat, level = 1)['contract_main'].loc['20180101':].iloc[:-1]
    #for date1 in ic_universe.index:
    def read_tick(date1):
        date = str(date1).replace('-', '')[:8]
        contract = ic_universe.loc[date1][:-4]
        _ = pd.read_csv('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/%s/%s.csv'%(contract, date)).set_index('dt')
        _.index = pd.to_datetime(_.index)
        _ = _.between_time('0925', '1457')
        _['amount'] = _['TotalValueTrade'].diff()
        _['volume'] = _['TotalVolumeTrade'].diff()
        _['vwap'] = _['amount']/r(_['volume'].copy()) / multiplier
        _['ret_1'] = _['vwap'].diff().shift(-2)
        _['ret_5'] = _['vwap'].diff(5).shift(-6)
        _['ret_10'] = _['vwap'].diff(10).shift(-11)
        _['ret_20'] = _['vwap'].diff(20).shift(-21)
        _['ret_30'] = _['vwap'].diff(30).shift(-31)
        _['ret_60'] = _['vwap'].diff(60).shift(-61)
        _['LastPx_diff'] = _['LastPx'].diff()
        _['LastPx_ret'] = _['LastPx'].pct_change()
        _['MidPx'] = (_['Buy1Price'] + _['Sell1Price']) / 2
        _['MidPx'][(_['MidPx'] < _['Buy1Price'] * 0.7) | (_['MidPx'] < _['Sell1Price'] * 0.7)] = np.nan
        _['MidPx_diff'] = _['MidPx'].diff()
        _['MidPx_ret'] = _['MidPx'].pct_change()
        return _

    date_list = sorted(list(ic_universe.index))

    with Pool(24) as pool:
        holder = pool.map(read_tick, date_list)

    tickdf = pd.concat(holder).sort_index()
    tickdf['vwap'][tickdf['vwap'].isna()] = tickdf['LastPx']
    #tickdf['vwap'] = tickdf['vwap'].fillna(method = 'ffill')

    tickdf1 = tickdf.copy()

    tickdf = pd.concat([tickdf.between_time('930', '1130'), tickdf.between_time('1300', '1457')])

    '''
    lastpx_volume_log = (abs(tickdf['LastPx_diff']) * ( np.log(tickdf['volume'] + 1))).resample('1min').sum()
    midpx_volume_log = (abs(tickdf['MidPx_diff']) * ( np.log(tickdf['volume'] + 1)) ).resample('1min').sum()
    pd.concat([lastpx_volume_log.between_time('0930', '1129'),lastpx_volume_log.between_time('1300', '1456')]).loc[siggg.index].to_pickle('/data/user/016700/Data/Factors/FILTERS/lastpx_log_volume_1%s.pkl'%trail)
    pd.concat([midpx_volume_log.between_time('0930', '1129'), midpx_volume_log.between_time('1300', '1456')]).loc[siggg.index].to_pickle('/data/user/016700/Data/Factors/FILTERS/midpx_log_volume_1%s.pkl'%trail)

    lastpx_volume = (abs(tickdf['LastPx_diff']) * ((tickdf['volume'] ))).resample('1min').sum()
    midpx_volume= (abs(tickdf['MidPx_diff']) * ( (tickdf['volume'] )) ).resample('1min').sum()
    pd.concat([lastpx_volume.between_time('0930', '1129'),lastpx_volume.between_time('1300', '1456')]).loc[siggg.index].to_pickle('/data/user/016700/Data/Factors/FILTERS/lastpx_volume%s.pkl'%trail)
    pd.concat([midpx_volume.between_time('0930', '1129'), midpx_volume.between_time('1300', '1456')]).loc[siggg.index].to_pickle('/data/user/016700/Data/Factors/FILTERS/midpx_volume%s.pkl'%trail)
    '''
    
    lastpx_volume_log = (abs(tickdf['LastPx_ret']) * ( np.log(tickdf['volume'] + 1))).resample('1min').sum()
    midpx_volume_log = (abs(tickdf['MidPx_ret']) * ( np.log(tickdf['volume'] + 1)) ).resample('1min').sum()
    pd.concat([lastpx_volume_log.between_time('0930', '1129'),lastpx_volume_log.between_time('1300', '1456')]).loc[siggg.index].to_pickle('/data/user/016700/Data/Factors/testing_purposes/ALL_CONTRACTS/pct_change/lastpx_ret_log_volume_1%s.pkl'%trail)
    pd.concat([midpx_volume_log.between_time('0930', '1129'), midpx_volume_log.between_time('1300', '1456')]).loc[siggg.index].to_pickle('/data/user/016700/Data/Factors/testing_purposes/ALL_CONTRACTS/pct_change/midpx_ret_log_volume_1%s.pkl'%trail)

    lastpx_volume = (abs(tickdf['LastPx_ret']) * ((tickdf['volume'] ))).resample('1min').sum()
    midpx_volume= (abs(tickdf['MidPx_ret']) * ( (tickdf['volume'] )) ).resample('1min').sum()
    pd.concat([lastpx_volume.between_time('0930', '1129'),lastpx_volume.between_time('1300', '1456')]).loc[siggg.index].to_pickle('/data/user/016700/Data/Factors/testing_purposes/ALL_CONTRACTS/pct_change/lastpx_ret_volume%s.pkl'%trail)
    pd.concat([midpx_volume.between_time('0930', '1129'), midpx_volume.between_time('1300', '1456')]).loc[siggg.index].to_pickle('/data/user/016700/Data/Factors/testing_purposes/ALL_CONTRACTS/pct_change/midpx_ret_volume%s.pkl'%trail)
        