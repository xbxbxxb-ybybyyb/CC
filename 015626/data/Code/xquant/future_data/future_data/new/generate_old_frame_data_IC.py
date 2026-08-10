import sys
sys.path.insert(4,'/data/user/015626/data/share/Code/factor_test/')
sys.path.insert(4,'/data/user/015626/data/share/Code/git_space/strategy_back_test/')
sys.path.insert(4,'/data/user/015626/data/share/Code/utils/')
sys.path.insert(4, '/data/user/015626/data/share/Code/git_space/futures-factor-framework/factor_framework/')
sys.path.insert(1,'/data/user/015626/JupyterNotebooks/utils/')
from data_center import DataCenter
from operators_all_wsc import *
from SIF_Factor_Test25 import *
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
import shutil
import bottleneck as bk
import random
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from pandas.testing import assert_frame_equal, assert_series_equal
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
pd.set_option('max_rows', 300)

ticker = 'IC.CFE'
start_date, end_date = 20180101, 20220630

save_rootpath = '/dfs/group/800466/warehouse/prod/MD/CHINA_FUTURES/MINUTE/INSAMPLE/'

suffix_dict = {'IC.CFE':500,'IF.CFE':300,'IH.CFE':50,'IM.CFE':1000}
tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50','IM.CFE':'index_weight_zz1000'}

savepath = os.path.join(save_rootpath, f'hf_data_{suffix_dict[ticker]}')
os.makedirs(savepath, exist_ok = True)

iw = IO.read_data(columns = [tickerdict[ticker]], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
iw = iw.unstack().shift(1).stack()
iw = iw.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
iw = iw[iw[tickerdict[ticker]] > 0]

stk_list = sorted(iw.index.get_level_values(1).unique().to_list())

col_list = IO.dipping(alt = '/dfs/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE/000001.SZ.h5').columns.tolist()

def get_stock(stock):
    iw_date = iw.xs(stock, level = 1)
    sdf = IO.read_data([iw_date.index[0].strftime('%Y%m%d'), udt.get_trading_day_offset(iw_date.index[-1].strftime('%Y%m%d'),1)[0].strftime('%Y%m%d')], columns = new_col_list, \
          alt = f'/dfs/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE/{stock}.h5')
    sdf = sdf.reset_index(level = 1, drop = True)
    sdf['date'] = sdf.index.date
    sdf = sdf[sdf['date'].isin(iw_date.index.date)]
    return (stock, sdf)

for i in tqdm(range(10, len(col_list) + 10, 10)):
    new_col_list = col_list[i-10: i]

    rlist = []
    with Pool(24) as pool:
        rlist = pool.map(get_stock, stk_list)
        
    for col in new_col_list:
        if os.path.exists(os.path.join(savepath, f'{col}_{suffix_dict[ticker]}.pkl')):
            continue
        new_rlist = []
        for xx in rlist:
            dd = xx[1][[col]]
            dd.columns = [xx[0]]
            new_rlist.append(dd)
        rdf = pd.concat(new_rlist, axis = 1, join= 'outer').sort_index()[stk_list]
        rdf.to_pickle(os.path.join(savepath, f'{col}_{suffix_dict[ticker]}.pkl'))