import sys
sys.path.insert(4,'/data/user/015626/data/share/Code/factor_test/')
sys.path.insert(4,'/data/user/015626/data/share/Code/git_space/strategy_back_test/')
sys.path.insert(4,'/data/user/015626/data/share/Code/utils/')
sys.path.insert(4, '/data/user/015626/data/share/Code/git_space/futures-factor-framework/factor_framework/')
sys.path.insert(1,'/data/user/015626/JupyterNotebooks/utils/')
# from data_center import DataCenter
from operators_all_wsc import *
from SIF_Factor_Test24 import *
import pandas as pd
import numpy as np
import datetime
import re, os, glob, math
from xquant.marketdata import MarketData as XMD
from xquant.thirdpartydata.marketdata import MarketData as XMDTP
import multifactor.utility.common as ut
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from multifactor.IO import IO
# from multifactor.IO import IO_old
from tqdm import tqdm
from multiprocessing import Pool
import dill, functools
pd.set_option('max_columns',100)
%matplotlib inline
import shutil
import bottleneck as bk
import random
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from pandas.testing import assert_frame_equal, assert_series_equal
import matplotlib.pyplot as plt
# from CHECK_PARA import *
# from back_test_tick_multisignal import *
import warnings
warnings.filterwarnings('ignore')
from xquant.factordata import FactorData
from xquant.futuredata import FutureData
fd = FutureData()
s = FactorData()
pd.set_option('max_rows', 300)

# dol = pd.read_csv('/data/user/015626/data/share/LOCAL_DATA/Mobius/ic2211.csv', index_col=0, parse_dates=True).add_suffix('_dol')
# minu = IO.read_data([20221103,20221104], columns = ['close','high','low','open'], alt='/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/IC_MINUTE.h5').xs('IC2211.CFE', level = 1)
# temp = dol.join(minu)
# temp[['close_dol','close']].plot(figsize = (10,5))
# ts_std(temp[['close_dol','close']].pct_change(),30).idxmax()
# temp[['close_dol','close']]
# temp.close_dol.corr(temp.close)
# temp.close_dol.shift(9).corr(temp.close)

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
# 将每日的时间戳固定为9:30-14:56
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

ma = XMD()

_,_,cdate_list = check_update_date(20250628,20250926)


df_list = []
for spot in ['000905.SH', '000852.SH', '000016.SH', '000300.SH', '399006.SZ', '000688.SH']:
    for date in tqdm(cdate_list):
        spot_ticker_dict = {'000905.SH':'IC.CFE', '000852.SH':'IM.CFE','000016.SH':'IH.CFE','000300.SH':'IF.CFE', '399006.SZ':'CYB', '000688.SH':'KC50'}
        tick = ma.get_data_by_date('index', spot, str(date))
        if len(tick) == 0:
            continue
        tick['LastPx'] = tick['LastPx'].replace(0, np.nan)
        tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        tick = tick.set_index('dt').resample('1min').agg({'LastPx':'mean'}).rename(columns = {'LastPx':'twap_spot'})
        tick = standard_index(tick).fillna(method = 'ffill')
        tick['Ticker'] = spot_ticker_dict[spot]
        df_list.append(tick)

df = pd.concat(df_list, axis = 0).sort_index()

df = df.reset_index().set_index(['dt','Ticker']).sort_index()

IO.pd_hdf5_writer(df, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/TWAP_SPOT.h5', dataset='TWAP_SPOT', append=True)