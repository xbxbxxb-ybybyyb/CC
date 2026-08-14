# @Time : 2020/12/21 9:59
# @Author : Zhichen Lu
# @File : load_vol_calc.py

import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from dataApi.getData import get_minute_1factor
from conf.path_config import deal_price_path, root_path
import pandas as pd
import numpy as np
from dataApi.usefulTools import frame2arr, ts_mean, arr2frame,ts_sum,delay
import copy,datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()
def shift_back(arr,l):
    arr[:-l] = arr[l:]
    arr[-l:] = np.nan
    return arr

lm.sendMessage('成交量更新开始')
start,end = 20160104,20181231
try:
    stock_pool = pd.read_pickle(root_path + 'stock_pool_without_limit_up_down.pkl').loc[start:end]
    vol = get_minute_1factor('vol', start_datetime=stock_pool.index[0] * 10000 + 925, end_datetime=stock_pool.index[-1] * 10000 + 1500,
                             code_list=stock_pool.columns.tolist()).fillna(0)
    window = 5
    vol_arr = frame2arr(vol)
    vol_rolling_30_sum_arr = ts_sum(vol_arr,window)
    vol_future_rolling_30_sum_arr = copy.deepcopy(vol_rolling_30_sum_arr)
    vol_future_rolling_30_sum_arr = shift_back(vol_future_rolling_30_sum_arr,window)

    vol_rolling_30_sum_5day_mean = ts_mean(vol_rolling_30_sum_arr.swapaxes(0, 1), 5).swapaxes(0, 1)

    vol_rolling_30_sum_5day_mean[:,1:,:] = vol_rolling_30_sum_5day_mean[:,:-1,:]
    vol_rolling_30_sum_5day_mean[:,:1,:] = np.nan
    vol_rolling_30_sum_5day = arr2frame(vol_rolling_30_sum_5day_mean, index=vol.index, columns=vol.columns.tolist())
    # vol_rolling_future_30min_sum_5day_mean = arr2frame(shift_back(vol_rolling_30_sum_5day_mean,30), index=vol.index, columns=vol.columns.tolist())
    vol_rolling_30_sum = arr2frame(vol_rolling_30_sum_arr, index=vol.index, columns=vol.columns.tolist())
    vol_future_rolling_30_sum = arr2frame(delay(vol_future_rolling_30_sum_arr), index=vol.index, columns=vol.columns.tolist())
    pd.to_pickle(vol_future_rolling_30_sum,deal_price_path+f'vol_future_rolling_{window}_sum.pkl')
    pd.to_pickle(vol_rolling_30_sum.loc[20160104:], deal_price_path + f'vol_rolling_{window}_sum.pkl')
    pd.to_pickle(vol_rolling_30_sum_5day.loc[20160104:], deal_price_path + f'vol_rolling_{window}_sum_5day_mean.pkl')
    # pd.to_pickle(vol_rolling_future_30min_sum_5day_mean.loc[20160104:], deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')


    # vol_rolling_30_suvol_rolling_30_summ = pd.read_pickle(deal_price_path + 'vol_rolling_30_sum.pkl')
    # vol_rolling_30_sum_5day = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
    lm.sendMessage('成交量更新完成----------------')
except:
    lm.sendMessage('成交量更新失败！！！！！！！！！！！！！！')