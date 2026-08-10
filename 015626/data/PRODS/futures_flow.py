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

def standard_index(data):
    t_days_list = udt.get_trading_date_range(str(data.index[0].date()).replace('-',''),str(data.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:56:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')

    data = index_df.join(data, how = 'left')
    return data

for cat in ['IF.CFE', 'IC.CFE', 'IM.CFE']:
    print(cat)
    if ('IC' in cat) :
        multiplier = 200
        trail = ''
        siggg = pd.read_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear/minute_raw/amount_sum_30_if.h5').loc['20180101':'20240123']

    elif ('IM' in cat):
        multiplier = 200
        trail = '_im'
        siggg = pd.read_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear/minute_raw/amount_sum_30_if.h5').loc['20220722':'20240123']



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
        _['pd'] = _['OpenInterest'].diff()
        _['主买'] = (_['LastPx'] > _['LastPx'].shift(1)).astype(int)
        _['主卖'] = (_['LastPx'] < _['LastPx'].shift(1)).astype(int)
        
        _['多开'] = ((_['LastPx'] > _['LastPx'].shift(1)) & (_['pd'] > 0)).astype(int)
        _['空平'] = ((_['LastPx'] > _['LastPx'].shift(1)) & (_['pd'] < 0)).astype(int)
        _['多换'] = ((_['LastPx'] > _['LastPx'].shift(1)) & (_['pd'] == 0)).astype(int)
        
        _['空开'] = ((_['LastPx'] < _['LastPx'].shift(1)) & (_['pd'] > 0)).astype(int)
        _['多平'] = ((_['LastPx'] < _['LastPx'].shift(1)) & (_['pd'] < 0)).astype(int)
        _['空换'] = ((_['LastPx'] < _['LastPx'].shift(1)) & (_['pd'] == 0)).astype(int)
              
        _['双开'] = ((_['LastPx'] == _['LastPx'].shift(1)) & (_['pd'] > 0)).astype(int)
        _['双平'] = ((_['LastPx'] == _['LastPx'].shift(1)) & (_['pd'] < 0)).astype(int)
        
        return standard_index(_[['主买', '主卖', '多开', '空平', '多换', '空开', '多平', '空换', '双开', '双平']].resample('1min').sum())

    date_list = sorted(list(ic_universe.index))

    with Pool(24) as pool:
        holder = pool.map(read_tick, date_list)

    tickdf = pd.concat(holder).sort_index()
    tickdf.to_pickle('/data/user/016700/Data/Factors/testing_purposes/FUTURES_FLOW/%s.pkl'%cat)