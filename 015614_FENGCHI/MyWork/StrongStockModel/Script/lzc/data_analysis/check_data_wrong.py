# @Time : 2020/9/28 9:36
# @Author : Zhichen Lu
# @File : check_data_wrong.py
import pandas as pd
from multiprocessing import Pool
from dataApi.tradeDate import get_date_range
from dataApi.getData import get_minute_1factor

stk_pool = pd.read_pickle('/data/group/800319/Faamonitor/ludashi.pkl')
signal = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num100_norm_window_40.pkl')

stk_pool.sum(axis=1).sort_values(ascending=False)
temp_pool = stk_pool.loc[20170605].sort_values(ascending=False)
temp_pool = temp_pool[temp_pool]

temp_signal = signal.loc[20170605]
temp_signal = temp_signal.loc[temp_pool.index]
