import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os
from multiprocessing import Pool
import time
from multifactor.data.utils import *

root_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE/'
target_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE_SH/'

standard_index = IO.read_data(columns = ['close','adjfactor'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE/000001.SZ.h5')
standard_index = standard_index.reset_index(level = 1).sort_index().index

def make_sh_per_stock(stock):
    try:
        result = pd.read_hdf(os.path.join(root_path,'%s.h5' % stock)).reset_index(level = 1).sort_index()
        result_index = result.index
        result = result.reindex(standard_index)

        stk_ret = (result['close'] * result['adjfactor'] / result.iloc[-1]['adjfactor']).pct_change(1, fill_method = None)

        index_data_sh50 = IO.read_data([20141229, 20220119], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_INDEX/MINUTE/000016.SH.h5')
        index_ret_sh50 = index_data_sh50['close'].xs('000016.SH', level = 1).pct_change(1, fill_method=None)
        result['stk_index_corr_sh50'] = stk_ret.rolling(1200, min_periods=600).corr(index_ret_sh50)
        result['stk_index_corr_sh50'] = result['stk_index_corr_sh50'].replace([-np.inf, np.inf], np.nan)

        result = result.reindex(result_index).reset_index().set_index(['dt','Ticker'])

        IO.pd_hdf5_writer(result, os.path.join(target_path,'%s.h5' % stock), dataset=stock)
    except:
        return
    
stock_list = [x[:-3] for x in os.listdir(root_path)]

with Pool(24) as pool:
    pool.map(make_sh_per_stock, stock_list)