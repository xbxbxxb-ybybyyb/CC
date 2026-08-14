import pandas as pd
import numpy as np
import IO
import os
from joblib import Parallel, delayed

def cut_by_basic(tradingday, basic_file_path, ori_path, out_path):
    print(tradingday)
    basic_file = IO.read_data([int(tradingday),int(tradingday)], columns = ['buy_time'], alt=basic_file_path)
    df = pd.read_pickle(f'{ori_path}{tradingday}.pkl', compression='gzip')
    df['buy_time'] = basic_file['buy_time'].apply(lambda x : int(x))
    df = df[df['MDTime'] < df['buy_time']]
    df.to_pickle(f'{out_path}{tradingday}.pkl', compression='gzip')
    return

basic_file_path = '/dfs/user/020412/团队分享/for_hotspot/md2_20250512_20150901_20231231.h5'
ori_path = '/dfs/user/015585/00_hotspot/trade_all_time35/'
out_path = '/dfs/user/015585/00_hotspot/TTransaction35/'
tradingday_list = os.listdir(ori_path)
tradingday_list = [i.replace('.pkl','') for i in tradingday_list if i[-3:] == 'pkl' ]
tradingday_list.sort()

factor_df_list = Parallel(n_jobs=24)(delayed(cut_by_basic)(tradingday, basic_file_path, ori_path, out_path) for tradingday in tradingday_list)

