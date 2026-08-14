# coding: utf-8
# Author：fengchi863
# Date ：2020/7/29 13:18

from StrongStockModel.conf.path_config import intraday_factor_by_date_path, root_path
from StrongStockModel.dataApi.getData import get_date_range
from StrongStockModel.dataApi.stockList import clean_stock_list
import pandas as pd, numpy as np, os
import time

start_date = 20170101
end_date = 20191231

date_list = get_date_range(start_date, end_date)
# pool = clean_stock_list(no_ST=False, least_live_days=1, least_recover_days=1, no_limit_up=True,
#                                 no_limit_down=True)
# stk_list = pool.columns.tolist()

out_path = root_path + 'factor/intraday_factor/'

def frame2arr(df, minutes=242):
    return df.values.reshape(df.shape[0] // minutes, minutes, df.shape[1]).transpose(1, 0, 2)

def wrapper(date):
    # if date == 20170110:
    #     break
    # if os.path.exists(out_path + '%d.npy' % date):
    #     return
    factor = pd.read_pickle(intraday_factor_by_date_path + '%d.pkl' % date)
    factor = factor[sorted(factor.columns.tolist())]
    factor = frame2arr(factor)
    print(date)
    print(factor.shape)
    np.save(out_path + '%d.npy' % date, factor)

from multiprocessing import Pool
pool = Pool(20)
pool.map_async(wrapper, date_list)
pool.close()
pool.join()

# 拼接
# e1 = time.time()
# # factor = np.r_['0,4', tuple(np.load(out_path + '%d.npy' % date) for date in date_list[0:5])]
# # print(time.time() - e1)
# # print(factor.shape)
