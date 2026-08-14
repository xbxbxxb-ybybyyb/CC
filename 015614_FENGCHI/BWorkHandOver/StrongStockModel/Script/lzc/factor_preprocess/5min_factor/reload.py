# @Time : 2020/10/14 13:34
# @Author : Zhichen Lu
# @File : reload.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from StrongStockModel.conf.path_config import root_path
import os
import pandas as pd
from dataApi.tradeDate import get_date_range
from dataApi.stockList import clean_stock_list
import gc
from multiprocessing import Pool
import numpy as np
from tqdm import tqdm
import datetime

N = 40
source_path = '/data/group/800319/junkBigFactor/'
preprocessed_ts_norm_by_factor_path = root_path + 'processed_factor_by_factor_5min/ts_norm_%d/'%N
preprocessed_by_date_path = root_path + 'processed_factor_all_pool_by_date_5min/ts_norm_%d_9_04_1_2_00/'%N
if not os.path.exists(preprocessed_by_date_path):
    os.mkdir(preprocessed_by_date_path)

# date_list = os.listdir(preprocessed_by_date_path)
# for date in date_list:
#     os.remove(preprocessed_by_date_path+date)

factor_list = os.listdir(preprocessed_ts_norm_by_factor_path)
factor_list = factor_list = list(filter(lambda x : x.startswith('00') or x.startswith('95') or x.startswith('91') or x.startswith('90') or
                                                   x.startswith('04') or x.startswith('1') or x.startswith('2'),factor_list))

factor_list = [x[:4] for x in factor_list]
factor_list.sort()
date_list = np.load(source_path+'date_list.npy').tolist()
stk_list = np.load(source_path+'code_list.npy').tolist()
stock_pool_path = root_path + 'stock_pool.pkl'
if not os.path.exists(stock_pool_path):
    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, start_date=20140101, end_date=20191231)
    h5_path = "/data/group/wdb_h5/WIND/universe_complete/universe_complete.h5"
    limit_info = {}
    limit_info['OPENUPLIMIT'] = pd.read_hdf(h5_path, 'OPENUPLIMIT')
    limit_info['OPENDOWNLIMIT'] = pd.read_hdf(h5_path, 'OPENDOWNLIMIT')
    for k in limit_info:
        limit_info[k] = limit_info[k].reset_index()
        limit_info[k]['dt'] = limit_info[k]['dt'].apply(lambda x: int(x.strftime('%Y%m%d')))
        limit_info[k]['Ticker'] = limit_info[k]['Ticker'].apply(lambda x: int(x[:-3]))
        limit_info[k] = limit_info[k].pivot_table(index='dt', columns='Ticker', values=k).reindex(stock_pool.index, axis=0).reindex(stock_pool.columns, axis=1).fillna(0) > 0

    stock_pool = stock_pool & limit_info['OPENUPLIMIT'] & limit_info['OPENDOWNLIMIT']
    pd.to_pickle(stock_pool,root_path+'stock_pool.pkl')
    print('saved')
else:
    stock_pool = pd.read_pickle(stock_pool_path)

def load_by_date(date):
    if os.path.exists(preprocessed_by_date_path + '%d.h5' % date):
        print(date, 'exist')
    factor_df_list = []
    start = date_list.index(date) * 48
    end = date_list.index(date) * 48 + 48
    temp_pool = stock_pool.loc[date]
    temp_stk_list = set(stk_list).intersection(temp_pool[temp_pool].index.tolist())
    for factor_name in factor_list:
        temp_df = pd.read_hdf(preprocessed_ts_norm_by_factor_path + '%s.h5' % factor_name, factor_name, start=start, stop=end)
        temp_df = temp_df[temp_stk_list].stack(dropna=False).to_frame()
        temp_df.columns = [factor_name]
        factor_df_list.append(temp_df)

    ###########
    """
    index_set = set(factor_df_list[0].index)
    bad = []
    good = []
    for i in range(len(factor_df_list)):
        each = factor_df_list[i]
        if set(each.index) != index_set:
            print(i,each.columns[0])
            bad.append(each)
            continue
        good.append(each)
    for each in bad:
        os.remove(preprocessed_ts_norm_by_factor_path + '%s.h5' % each.columns[0])
    """
    ###########
    factor_df = pd.concat(factor_df_list, axis=1)
    factor_df.index = factor_df.index.swaplevel(1, 2)
    factor_df = factor_df.sort_index()
    factor_df.to_hdf(preprocessed_by_date_path + '%d.h5' % date, '%d' % date, format='t')
    del factor_df, factor_df_list
    gc.collect()
    print(date, 'done')

def wraper(date):
    if os.path.exists(preprocessed_by_date_path + '%d.h5' % date):
        print(date,'exist')
        return True
    try:
        load_by_date(date)
        return True
    except:
        print(date,'Wrong')
        pd.DataFrame().to_csv(preprocessed_by_date_path + '%d.csv' % date)
        return False

load_by_date(20171220)
#date_list = list(filter(lambda x: not os.path.exists(preprocessed_by_date_path + '%d.h5' % x), date_list))
# load_by_date(date_list[154])




# partition = 5
# idx = 5
# file_list = list(filter(lambda x : not os.path.exists(preprocessed_by_date_path + '%d.h5' % date),date_list))
# file_list = file_list[(idx-1)*len(file_list)//partition:idx*len(file_list)//partition]
# pbar = tqdm(total=len(file_list))
# def update(*param):
#     pbar.update()
#     pbar.set_description('preprocessing %d |%s|%s' % (idx,str(file_list[pbar.last_print_n - 1]), datetime.datetime.now().strftime('%H:%M:%S')))
#     if pbar.last_print_n == len(file_list):
#         pbar.close()
#
# pool = Pool(24)
# pool_dict = {}
# for date in file_list:
#     pool_dict[date] = pool.apply_async(wraper,(date,),callback=update)
# # pool.map(load_by_date, date_list)
# pool.close()
# pool.join()
#
# for date in pool_dict:
#     pool_dict[date] = pool_dict[date].get()
#     if not pool_dict[date]:
#         print(date,'Wrong')



