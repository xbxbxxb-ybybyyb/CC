# @Time : 2021/12/22 10:37
# @Author : Zhichen Lu
# @File : IntradayLabel.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
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
import os
import shutil

class ArrReshape(object):

    def to2d(self, arr):
        self.freq = arr.shape[1]
        if arr.dtype == np.float:
            arr = np.round(arr, 8)
        return arr.reshape(arr.shape[0] * arr.shape[1], arr.shape[2])

    def to3d(self, arr):
        if arr.dtype == np.float:
            arr = np.round(arr, 8)
        return arr.reshape(arr.shape[0] // self.freq, self.freq, arr.shape[1])

def dt_beta2(x, y, m3):
    x = x.copy()
    y = y.copy()
    shape = x.shape
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    f = np.isfinite(x) & np.isfinite(y)
    x[~ f] = 0
    y[~ f] = 0
    cx = bottleneck.move_sum(x.sum(axis=1), m3, axis=0)
    cy = bottleneck.move_sum(y.sum(axis=1), m3, axis=0)
    cx2 = bottleneck.move_sum((x ** 2).sum(axis=1), m3, axis=0)
    cxy = bottleneck.move_sum((x * y).sum(axis=1), m3, axis=0)
    cn = bottleneck.move_sum((f.astype('float32')).sum(axis=1), m3, axis=0)
    a = (cn * cxy - cx * cy)
    b = (cn * cx2 - cx ** 2)
    beta = a / b  # np.divide(a, b, out=np.full(x.shape, np.nan), where=abs(b) > 1e-8)
    beta[cn < m3 / 2] = np.nan
    # beta = ar.to3d(beta)
    alpha = cy / cn - cx * beta / cn
    return alpha.reshape(shape[:2]), beta.reshape(shape[:2])

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

def get_nolimit(test_date_list, code_list):

    nolimit = get_minute_pickle('limit_status', test_date_list, code_list).values == 0
    nolimit = nolimit.reshape(len(test_date_list), 242, len(code_list))[
              :, [trade_minutes.index(x) for x in period_list]]
    nolimit = nolimit.transpose(0, 2, 1)
    return nolimit

def get_future_by_30min(test_date_list, code_list,future_bar=1, delay_min=1, order_keep_min=30):
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
    future = future.transpose(0, 2, 1)
    return future


def save_bar_future(start,end,f_bar,out_path,order_keep_min,reg_len):
    print(f'Bar_num {f_bar}')
    out_file = f'{out_path}future_{f_bar}_bar_regW{reg_len}barly.npy'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    if os.path.exists(out_file):
        print(f'Bar_num {f_bar} exist')
        # return
    for each in ['idx_date.npy', 'idx_time.npy', 'idx_code.npy', 'future.npy', 'nolimit.npy']:
        shutil.copy(f'/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/{each}',
                    f'{out_path}/{each}')
    code_list = get_all_stock_ever_appear(end)
    date_list = get_date_range(get_pre_trade_date(start), end)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, period_list)))
    future_short_window = get_future_by_30min(date_list, code_list, future_bar=f_bar, delay_min=1, order_keep_min=order_keep_min)
    recent_pct_change = get_recent_pct_change(date_list,code_list,future_days=1,delay_min=-2,order_keep_min=1)
    # future_short_window.shape
    recent_pct_change = recent_pct_change.transpose(0,2,1)
    alpha,beta = dt_beta2(x=recent_pct_change,y=future_short_window[:,1:,:],m3=reg_len)
    alpha,beta = [np.pad(x,((2,0),(0,0)),constant_values=np.nan,mode='constant') for x in [alpha[:-2,:],beta[:-2,:]]]
    y_ht = alpha[:,:,None] + beta[:,:,None] * recent_pct_change
    future_res = future_short_window[:,1:,:] - y_ht
    future_short_window = np.pad(future_res,((0,0),(1,0),(0,0)),constant_values=np.nan,mode='constant')
    future_short_window_df = pd.DataFrame(future_short_window.reshape(len(date_list) * len(period_list), len(code_list)), index=index, columns=code_list)
    future_short_window_df = future_short_window_df.swaplevel(0,1).loc[out_period_list].swaplevel(0,1).sort_index()
    target_index = pd.MultiIndex.from_tuples(list(itertools.product(date_list+[get_pre_trade_date(date_list[-1],-1)],out_period_list)))
    future_short_window_df = future_short_window_df.reindex(target_index)
    future_short_window_df.loc[get_pre_trade_date(end,-1)] = 0
    # future_short_window_df.loc[get_pre_trade_date(date_list[-1],-1)] = np.nan
    future_short_window_arr = trans_df2arr(future_short_window_df, start_date=start, end_date=get_pre_trade_date(end,-1), roll=True)
    future_short_window_arr = np.ascontiguousarray(future_short_window_arr.astype('float32'))
    np.save(out_file, future_short_window_arr)
    print(out_file,future_short_window_df)
# pool = get_stock_pool(date_list)

# code_list = pool.columns.tolist()

period_list = [930,1000, 1030, 1100, 1300, 1330, 1400, 1430]
out_period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]

from xquant.compute.aimr import AIMR
future_bar = 8#int(AIMR.getParam())
latest_day = 20220524#get_pre_trade_date(get_recent_trade_date())
save_bar_future(20140801,latest_day,f_bar=future_bar,
                out_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5ReversalRes/data/',order_keep_min=5,
                reg_len=1)



# for future_bar in list(range(1,9)):
#     save_bar_future(20140801,20220216,f_bar=future_bar,out_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/',order_keep_min=5)
#     print(future_bar,'done')



# from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering,load_fix_data_selfdefined_label
# import pandas as pd
# from dataApi.getData import get_minute_1factor
#
# X, y, nolimit_, idx_date, idx_code, idx_time = load_fix_data(20220112,20220303,factor_list=['future_2_bar'],address='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/')
#
# X, y, nolimit_, idx_date, idx_code, idx_time,y_1day = load_fix_data_selfdefined_label(20220112,20220303,factor_list=['CRCS_raw_rank_skew10'],
#                     label_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/future_2_bar.npy',return_1day_label=True)
# X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit_, idx_date, idx_code, idx_time)
# index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
# X = pd.Series(X[:,0],index=index).unstack()
# y =pd.Series(y,index=index).unstack()

# close_badj = get_minute_1factor('close_badj', start_datetime=20161221, end_datetime=20161231)
# close_badj = close_badj.swaplevel(0, 1).loc[close_badj.index.levels[1][1:-1]].swaplevel(0, 1)
# future_clac = close_badj.pct_change(30).shift(-31)
# future_clac = future_clac.swaplevel(0, 1).loc[out_period_list].swaplevel(0, 1)
#
#
