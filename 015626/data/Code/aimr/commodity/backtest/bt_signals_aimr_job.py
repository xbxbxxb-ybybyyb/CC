from xquant.compute.aimr import AIMR
para_list=eval(AIMR.getParam())
print(para_list)

import sys
sys.path.insert(4, '/dfs/user/015626/JupyterNotebooks/utils/')
sys.path.insert(4, '/data/user/015626/data/Code/git_space/strategy_back_test/commodity/')

import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import itertools
import multifactor.utility.dt as udt
import warnings
from multiprocessing import Pool
from utility import concurrent_apply_func

from ts_backtest_minute_com import *

import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 

signame = para_list[0]
sig_pkl_name = para_list[1]
is_filter = False
start_date = '20180101'
end_date = '20221231'

backtest_name = 'all69_3e7std'
backtest_name = backtest_name + '_basis' if is_filter else backtest_name
initial_cash = 3e6

long_t = 0.05
short_t = 0.05
super_t = 0.15

flag = True
ac_df = pd.read_csv('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/zf_all_aclist_new.csv', index_col=0)['ac_60']
ac = ac_df.loc[sig_pkl_name]
if ac < 0.4:
    flag = False
elif ac >= 0.4 and ac < 0.75:
    univ_name = 'cost_100_univ'
elif ac >= 0.75 and ac < 0.85:
    univ_name = 'cost_300_univ'
elif ac >= 0.85 and ac < 0.95:
    univ_name = 'cost_500_univ'
elif ac >= 0.95 and ac < 0.975:
    univ_name = 'cost_1000_univ'
elif ac >= 0.975 and ac < 0.985:
    univ_name = 'cost_1500_univ'
elif ac >= 0.985:
    univ_name = 'cost_2000_univ'

if flag:
    univ = IO.read_data([str(start_date), str(end_date) + '235959'], columns=[univ_name], alt = '/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/UNIVERSE/CHINA_COMMODITY_UNIVERSE_MINUTE.h5')
    univ = univ[univ_name]

    sig_rootpath = '/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/zf_all/'
    if int(end_date) > 20231231:
        sig_rootpath = '/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/zf_all_oos/'

    sig_pkl_name_list = [x.replace('.pkl', '') for x in os.listdir(sig_rootpath) if x.startswith(signame)]

    if is_filter:
        basis_raw_dict = pd.read_pickle('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/wyc/basis_raw_all.pkl')
        basis_raw_mean1y_dict = pd.read_pickle('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/wyc/basis_raw_mean1y_all.pkl')

    def get_sig_pkl_name(sig_pkl_name):
        sig_pkl = pd.read_pickle(os.path.join(sig_rootpath, f'{sig_pkl_name}.pkl'))
        rdict = {}
        para_name = sig_pkl_name.replace(f'{signame}_', '')
        _save_path = f"/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/wyc/back_test_new/{backtest_name}/{signame}/{start_date}_{end_date}/{para_name}"
        if os.path.exists(os.path.join(_save_path, 'result.pkl')):
            return   
        for ticker in sig_pkl.keys():
            try:
                signal = sig_pkl[ticker].iloc[:, 0]
                if len(signal.loc[start_date:end_date].dropna()) == 0:
                    print(ticker, 'lenth is 0')
                    continue
                _univ = univ.xs(ticker, level = 1)
            
                filter_series = pd.Series(0, index = signal.index)
                filter_series.loc[(signal>0) & (_univ==True)] = 1
                filter_series.loc[(signal<0) & (_univ==True)] = -1
            
                if is_filter:
                    basis_raw = basis_raw_dict[ticker]['basis_raw'].copy().loc[str(start_date):str(end_date)]
                    basis_raw_mean1y = basis_raw_mean1y_dict[ticker]['basis_raw'].copy().loc[str(start_date):str(end_date)]
                    
                    filter_series.loc[(((basis_raw_mean1y < -long_t) & (basis_raw < -short_t)) | (basis_raw < -super_t))  & (signal < 0)] = 0
                    filter_series.loc[(((basis_raw_mean1y > long_t) & (basis_raw > short_t)) | (basis_raw > super_t)) & (signal > 0)] = 0
            
                name_prefix = ticker
                bto = TS_BACK_TEST(signal, ticker = ticker, initial_cash=initial_cash, price_kind='twap', 
                                 c_rate=0.0004, slippage=0, std_filter_threshold = 0,
                                 pos_dict = {(0,   0.1): (0.0, 0.0),
                                             (0.1, 0.2): (0,   0.5),
                                             (0.2, 0.8): (0,   1),
                                             (0.8, 0.9): (0.5, 1),
                                             (0.9, 100): (1,   1)},
                                 filter_series = filter_series,
                                stop_loss = -100, start_date = start_date, end_date = end_date,deal_volume_ratio = 0.3,
                                open_num_permin=1e8, close_num_permin=1e8,minute_after_stop_loss=10,max_hold_time=None,
                                trading_range = None,
                                save_path = _save_path,
                                name_prefix = name_prefix, save_csv = False, show_image = False, save_image = True)
                
                result = bto.back_test()
                rdict[ticker] = result
                del(bto)
            except Exception as e:
                print(sig_pkl_name_list, e)
        save_pickle(rdict, os.path.join(_save_path, 'result.pkl'))
        
    get_sig_pkl_name(sig_pkl_name)