# @Time : 2020/8/24 8:45
# @Author : Zhichen Lu
# @File : factor_preprocessing.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from StrongStockModel.conf.path_config import root_path#, preprocessed_ts_norm_by_factor_path
import os
import pandas as pd
from StrongStockModel.dataApi.TrueSendFactorTest import _get_fix_factor_list
from dataApi.tradeDate import get_date_range
from System.LoadFactor.FactorDataSet import FactorDataSet
from dataApi.stockList import clean_stock_list
import gc
from multiprocessing import Pool
import time
from tqdm import tqdm
import datetime

N = 40
preprocessed_ts_norm_by_factor_path =  root_path + 'processed_factor_by_factor/ts_norm_%d_out_of_sample/' % N
preprocessed_by_date_path = root_path + 'processed_factor_all_pool_by_date/ts_norm_%d/' % N
if not os.path.exists(preprocessed_by_date_path):
    os.mkdir(preprocessed_by_date_path)


factor_list = _get_fix_factor_list()
date_list = get_date_range(20190701,20201103)
fsd = FactorDataSet(start_date=20140101, end_date=20201031)
fix_factor_list = list(fsd.fix_factor_dict.keys())
stk_list = list(fsd.stk_dict.keys())
stock_pool_path = root_path + 'stock_pool_without_limit_up_down.pkl'
if not os.path.exists(stock_pool_path):
    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, start_date=20140101, end_date=20201031)
    h5_path = "/data/group/wdb_h5/WIND/universe_complete/universe_complete.h5"
    limit_info = {}
    limit_info['OPENUPLIMIT'] = pd.read_hdf(h5_path, 'OPENUPLIMIT')
    limit_info['OPENDOWNLIMIT'] = pd.read_hdf(h5_path, 'OPENDOWNLIMIT')
    for k in limit_info:
        limit_info[k] = limit_info[k].reset_index()
        limit_info[k]['dt'] = limit_info[k]['dt'].apply(lambda x: int(x.strftime('%Y%m%d')))
        limit_info[k]['Ticker'] = limit_info[k]['Ticker'].apply(lambda x: int(x[:-3]))
        limit_info[k] = limit_info[k].pivot_table(index='dt', columns='Ticker', values=k).reindex(stock_pool.index, axis=0).reindex(stock_pool.columns, axis=1).fillna(0) > 0

    limit_info['OPENUPLIMIT'].loc[20191203:] = True
    limit_info['OPENDOWNLIMIT'].loc[20191203:] = True
    stock_pool = stock_pool & limit_info['OPENUPLIMIT'] & limit_info['OPENDOWNLIMIT']
    pd.to_pickle(stock_pool, root_path + 'stock_pool_without_limit_up_down.pkl')
    print('saved')
else:
    stock_pool = pd.read_pickle(stock_pool_path)

def load_by_date(date):
    if os.path.exists(preprocessed_by_date_path + '%d.h5' % date):
        print(date, 'exist')
        return
    factor_df_list = []
    start = date_list.index(date) * 7
    end = date_list.index(date) * 7 + 7
    temp_pool = stock_pool.loc[date]
    temp_stk_list = set(stk_list).intersection(temp_pool[temp_pool].index.tolist())
    for factor_name in factor_list:
        temp_df = pd.read_hdf(preprocessed_ts_norm_by_factor_path + '%s.h5' % factor_name, factor_name, start=start, stop=end)
        temp_df = temp_df[temp_stk_list].stack(dropna=False).to_frame()
        temp_df.columns = [factor_name]
        factor_df_list.append(temp_df)

    factor_df = pd.concat(factor_df_list, axis=1)
    factor_df.index = factor_df.index.swaplevel(1, 2)
    factor_df = factor_df.sort_index()
    factor_df.to_hdf(preprocessed_by_date_path + '%d.h5' % date, '%d' % date, format='t')
    del factor_df, factor_df_list
    gc.collect()
    print(date, 'done')


def wraper(date):
    if os.path.exists(preprocessed_by_date_path + '%d.h5' % date):
        print(date, 'exist')
        return True
    try:
        load_by_date(date)
        return True
    except:
        print(date, 'Wrong')
        pd.DataFrame().to_csv(preprocessed_by_date_path + '%d.csv' % date)
        return False


# date_list = list(filter(lambda x: not os.path.exists(preprocessed_by_date_path + '%d.h5' % x), date_list))
# wraper(date_list[20])
# load_by_date(20200414)

# file_list = list(filter(lambda x : not os.path.exists(preprocessed_by_date_path + '%d.h5' % x),date_list))

pbar = tqdm(total=len(date_list))


def update(*param):
    pbar.update()
    pbar.set_description('preprocessing %d |%s|%s' % (N, str(date_list[pbar.last_print_n - 1]), datetime.datetime.now().strftime('%H:%M:%S')))
    if pbar.last_print_n == len(date_list):
        pbar.close()

pool = Pool(24)
pool_dict = {}

for date in date_list:
    pool_dict[date] = pool.apply_async(wraper, (date,), callback=update)
# pool.map(load_by_date, date_list)
pool.close()
pool.join()

for date in pool_dict:
    pool_dict[date] = pool_dict[date].get()
    if not pool_dict[date]:
        print(date, 'Wrong')

