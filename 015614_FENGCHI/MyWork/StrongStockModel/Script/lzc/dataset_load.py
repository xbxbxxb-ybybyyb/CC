# @Time : 2020/8/13 13:48
# @Author : Zhichen Lu
# @File : dataset_load.py

import pandas as pd
import numpy as np
from StrongStockModel.conf.path_config import intraday_factor_path, fix_factor_by_date_path, intraday_factor_by_date_path, root_path, strong_stock_path, ghost_stock_path, root_path
from StrongStockModel.System.LoadFactor.FactorDataSet import FactorDataSet
from StrongStockModel.System.LoadLabel.LabelDataSet import LabelDataSet
from StrongStockModel.dataApi.getData import get_date_range
import os
from multiprocessing import Pool
import time
import gc


fsd = FactorDataSet(start_date=20140101, end_date=20181231)
fix_factor_list = list(fsd.fix_factor_dict.keys())
stk_list = list(fsd.stk_dict.keys())

lds = LabelDataSet(start_date=20140101, end_date=20201031)
label_path = root_path + 'labels/'
if not os.path.exists(label_path):
    os.mkdir(label_path)

stock_pool = pd.read_pickle(strong_stock_path)
# strong_pool = pd.read_pickle(ghost_stock_path)
stock_pool.columns = [int(x[:-3]) for x in stock_pool.columns]
stock_pool.index = stock_pool.index.astype(int)

stk_list = list(set(stk_list).intersection(set(stock_pool.columns)))
stock_pool = stock_pool[stk_list]

"""
# 标签预存储
pct_change = lds.calc_pctchg_N(start_date=20140101, end_date=20201031, address=None)

base_date_list = get_date_range(20140101, 20201031)
target_index = list(filter(lambda x: x[1] in [1000, 1030, 1100, 1300, 1330, 1400, 1430], pct_change.index.tolist()))
pct_change = pct_change.loc[target_index]
pct_change[pct_change == np.inf] = np.nan
pct_change[pct_change == -np.inf] = np.nan
pct_change.index = pd.MultiIndex.from_tuples(pct_change.index.tolist())
pct_change.sort_index().to_hdf(label_path + 'pct_240m.h5', 'pct_240m', format='t')
"""


# from dataApi.getData import get_minute_1factor
# close_adj = get_minute_1factor('close_badj',20150105,20150106,code_list=[1])
# close_adj.swaplevel(0,1).loc[[1100]]


def clear_path(path):
    file_list = os.listdir(path)
    for file_name in file_list:
        os.remove(path + file_name)


out_path = '/data/group/800319/junkData/StrongStock/factor/strong_pool_fix_factor_preprocessed_ts_norm/'
preprocessed_by_date_path = root_path + 'processed_factor_by_date/ts_norm/'
if not os.path.exists(out_path):
    os.mkdir(out_path)


def out_wraper(date):
    if os.path.exists(out_path + '%d.pkl' % date):
        print(date, 'exist')
        return
    temp_stk_list = stock_pool.loc[date]
    temp_stk_list = temp_stk_list[temp_stk_list].index.tolist()
    stk_list = list(set(temp_stk_list).intersection(fsd.stk_list))
    try:
        data = fsd.load_fix_factor_h5(stk_list, fix_factor_list, date, factor_address=preprocessed_by_date_path)
        pd.to_pickle(data, out_path + '%d.pkl' % date)
        del data
        gc.collect()
        print(date, len(stk_list), 'done')
    except:
        print(date, 'Wrong')
    return True


# out_wraper(fsd.date_list[0])
i = 0
while True:
    if i >= 10:
        break
    target_list = list(filter(lambda x: os.path.exists(preprocessed_by_date_path + '%d.h5' % x), fsd.date_list))
    if len(target_list) == 0:
        time.sleep(60)
        i += 1
        continue
    pool = Pool(10)
    pool.map(out_wraper, target_list)
    pool.close()
    pool.join()
    i = 0
