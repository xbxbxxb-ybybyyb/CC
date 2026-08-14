# @Time : 2020/10/20 14:03
# @Author : Zhichen Lu
# @File : BinaryFeatureProcess.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import os
import pandas as pd
from dataApi.tradeDate import get_date_range
from conf.path_config import root_path
from multiprocessing import Pool
import gc
from System.LoadFactor.FactorDataSet import FactorDataSet
from tqdm import tqdm
import datetime
preprocessed_ts_norm_by_factor_path = '/data/group/800319/wyl/factor30m/'
preprocessed_by_date_path = root_path + 'processed_factor_all_pool_by_date/binary_feature/'

date_list = get_date_range(20140101, 20181231)
check = pd.read_hdf(preprocessed_by_date_path+'20140102.h5','20140102')
print(check.columns.tolist())
if not os.path.exists(preprocessed_by_date_path):
    os.mkdir(preprocessed_by_date_path)

factor_list = [x.replace('.h5','') for x in os.listdir(preprocessed_ts_norm_by_factor_path)]
date_list = get_date_range(20140101, 20181231)
fsd = FactorDataSet(start_date=20140101, end_date=20191231)
fix_factor_list = list(fsd.fix_factor_dict.keys())
stk_list = list(fsd.stk_dict.keys())
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
    pd.to_pickle(stock_pool, root_path + 'stock_pool.pkl')
    print('saved')
else:
    stock_pool = pd.read_pickle(stock_pool_path)

def load_by_date(date):
    if os.path.exists(preprocessed_by_date_path + '%d.h5' % date):
        print(date, 'exist')
    factor_df_list = []
    start = date_list.index(date) * 8
    end = date_list.index(date) * 8 + 8
    temp_pool = stock_pool.loc[date]
    temp_stk_list = set(stk_list).intersection(temp_pool[temp_pool].index.tolist())
    for factor_name in factor_list:
        temp_df = pd.read_hdf(preprocessed_ts_norm_by_factor_path + '%s.h5' % factor_name, factor_name, start=start, stop=end)[:7]
        temp_df = temp_df[temp_stk_list].stack(dropna=False).to_frame()
        temp_df.columns = [factor_name]
        factor_df_list.append(temp_df)
    factor_df = pd.concat(factor_df_list, axis=1)
    factor_df.index = pd.MultiIndex.from_tuples([(int(x[0][:8]),x[1],int(x[0][8:])) for x in factor_df.index])
    # factor_df.index = factor_df.index.swaplevel(1, 2)
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
load_by_date(20171221)
# wraper(date_list[0])

pbar = tqdm(total=len(date_list))


def update(*param):
    pbar.update()
    pbar.set_description('preprocessing %d |%s|%s' % (0, str(date_list[pbar.last_print_n - 1]), datetime.datetime.now().strftime('%H:%M:%S')))
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
