# @Time : 2021/12/22 10:37
# @Author : Zhichen Lu
# @File : IntradayLabel.py

import sys
from dataApi.tradeDate import get_date_range, get_pre_trade_date, trade_minutes, get_sub_date_index, \
    get_desample_minute_dict, get_trade_date_interval, get_recent_trade_date
from dataApi.getData import get_daily_1factor
from dataApi.stockList import clean_stock_list, trans_windcode2int,get_all_stock_ever_appear
import numpy as np
from dataApi.getData import get_minute_pickle,get_minute_1factor
import pandas as pd
import bottleneck
import gc
from dataApi.LoadingTool import trans_df2arr
import itertools
from tqdm import tqdm

def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)

def find_trade_min(sign_min, delay_min=1, order_keep_min=5):
    sign_min = sign_min if sign_min < 242 else trade_minutes.index(sign_min)
    trade_min = [sign_min + delay_min + x for x in range(order_keep_min)]
    if trade_min[0] >= 241:
        trade_min = [242]
    elif trade_min[-1] >= 238:
        trade_min = list(range(min(trade_min[0], 238), 242))
    if len(trade_min) > order_keep_min:
        trade_min = trade_min[:order_keep_min - 1] + [241]
    elif trade_min == [242]:
        trade_min = [242] * order_keep_min
    elif len(trade_min) < order_keep_min:
        trade_min = trade_min + [241] * (order_keep_min - len(trade_min))
    return trade_min

def get_recent_pct_change(test_date_list, code_list, future_days=1, delay_min=1, order_keep_min=5):
    period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    future_start_date = get_pre_trade_date(test_date_list[0], future_days)
    future_date_list = get_date_range(future_start_date,test_date_list[-1])
    future = get_minute_pickle('close_adj', future_date_list, code_list)
    test_date_num = len(test_date_list)
    idx = np.arange(test_date_num + future_days)[:, None, None] * 242 + np.asanyarray([find_trade_min(
        x, delay_min, order_keep_min) for x in period_list])[None, :, :]
    future = np.nanmean(future.values[idx], axis=2)
    future = future[future_days:test_date_num+future_days]/future[: test_date_num ]  - 1
    # future = future.transpose(0, 2, 1)
    return future

def get_nolimit(test_date_list, code_list):
    period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    nolimit = get_minute_pickle('limit_status', test_date_list, code_list).values == 0
    nolimit = nolimit.reshape(len(test_date_list), 242, len(code_list))[
              :, [trade_minutes.index(x) for x in period_list]]
    nolimit = nolimit.transpose(0, 2, 1)
    return nolimit


def get_future(test_date_list, code_list, future_days=1, delay_min=1, order_keep_min=5):
    period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    future_end_date = get_pre_trade_date(test_date_list[-1], - future_days)
    future_date_list = get_date_range(test_date_list[0], future_end_date)
    future = get_minute_pickle('close_adj', future_date_list, code_list)
    test_date_num = len(test_date_list)
    idx = np.arange(test_date_num + future_days)[:, None, None] * 242 + np.asanyarray([find_trade_min(
        x, delay_min, order_keep_min) for x in period_list])[None, :, :]
    # idx = np.arange(test_date_num + future_days)[:, None, None] * 242 + np.array([[31]])[None, :, :]
    future = np.nanmean(future.values[idx], axis=2)
    future = future[future_days: test_date_num + future_days] / future[:test_date_num] - 1
    # future[43]
    # future = future.transpose(0, 2, 1)
    return future


def get_future_by_30min(test_date_list, code_list,future_bar=1, delay_min=1, order_keep_min=30):
    period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    future_end_date = get_pre_trade_date(test_date_list[-1], - 1)
    future_date_list = get_date_range(test_date_list[0], future_end_date)
    close_badj = get_minute_pickle('close_adj', future_date_list, code_list)
    test_date_num = len(test_date_list)
    idx = np.arange(test_date_num + 1)[:, None, None] * 242 + np.asanyarray([find_trade_min(
        x, delay_min, order_keep_min) for x in period_list])[None, :, :]
    # idx = np.arange(test_date_num + future_days)[:, None, None] * 242 + np.array([[31]])[None, :, :]
    close_badj = np.nanmean(close_badj.values[idx], axis=2)
    close_badj_append =np.concatenate([close_badj[:-1],close_badj[1:]],axis=1)
    future = close_badj_append[:,future_bar:len(period_list)+future_bar,:]/close_badj_append[:,:len(period_list),:] - 1
    return future


def save_recent_pct(start,end):
    code_list = get_all_stock_ever_appear(end)
    date_list = get_date_range(get_pre_trade_date(start), end)
    recet_pct_change = get_recent_pct_change(date_list, code_list)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, [1000, 1030, 1100, 1300, 1330, 1400, 1430])))
    recet_pct_change = pd.DataFrame(recet_pct_change.reshape(len(date_list) * 7, len(code_list)), index=index, columns=code_list)
    recet_pct_change = trans_df2arr(recet_pct_change, start_date=start, end_date=end, roll=True)
    recet_pct_change = np.ascontiguousarray(recet_pct_change.astype('float32'))
    np.save('/data/group/800442/800319/HFfactor/ForDerivativeLabel/data/rct_pct.npy', recet_pct_change)

def save_bar_future(start,end,f_bar):
    code_list = get_all_stock_ever_appear(end)
    date_list = get_date_range(get_pre_trade_date(start), end)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, [1000, 1030, 1100, 1300, 1330, 1400, 1430])))
    future_short_window = get_future_by_30min(date_list, code_list, future_bar=f_bar, delay_min=1, order_keep_min=5)
    future_short_window_df = pd.DataFrame(future_short_window.reshape(len(date_list) * 7, len(code_list)), index=index, columns=code_list)
    future_short_window_arr = trans_df2arr(future_short_window_df, start_date=start, end_date=end, roll=True)
    future_short_window_arr = np.ascontiguousarray(future_short_window_arr.astype('float32'))
    np.save(f'/data/group/800442/800319/HFfactor/ForDerivativeLabel/data/future_{f_bar}_bar.npy', future_short_window_arr)
    print(f'/data/group/800442/800319/HFfactor/ForDerivativeLabel/data/future_{f_bar}_bar_5m.npy')
# pool = get_stock_pool(date_list)

# code_list = pool.columns.tolist()




for future_bar in [7]:
    save_bar_future(20140801,20211220,f_bar=future_bar)



from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering,load_fix_data_selfdefined_label
import pandas as pd

def check_data(factor_list,add):
    X, y, nolimit_, idx_date, idx_code, idx_time = load_fix_data(20161221,20161231,factor_list=factor_list,address=add)
    X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit_, idx_date, idx_code, idx_time)
    index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
    X = pd.Series(X[:,0],index=index).unstack()
    y =pd.Series(y,index=index).unstack()
    X_ = X.head(50)
    y_ = y.head(50)
    return X_,y_

old_X,old_y = check_data(['future_1_bar'],'/data/group/800442/800319/HFfactor/ForDerivativeLabel/data/')
new_X,new_y = check_data(['HF_VolumeAmtSkewRatio'],'/data/group/800442/800319/HFfactor/RealTimeFixRollRobustReversalRes/data/')
new_val_X,new_val_y = check_data(['HF_VolumeAmtSkewRatio'],'/data/group/800442/800319/HFfactor/RealTimeFixRollRobustReversalResVal/data/')


X, y, nolimit_, idx_date, idx_code, idx_time = load_fix_data_selfdefined_label(20161221,20161231,factor_list=['HF_VolumeAmtSkewRatio'],label_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel/data/future_1_bar.npy')
X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit_, idx_date, idx_code, idx_time)
index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
X = pd.Series(X[:,0],index=index).unstack()
y =pd.Series(y,index=index).unstack()