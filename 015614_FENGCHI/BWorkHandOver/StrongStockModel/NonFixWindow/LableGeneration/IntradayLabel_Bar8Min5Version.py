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



def save_bar_future(start,end,f_bar,out_path,order_keep_min):
    print(f'Bar_num {f_bar}')
    out_file = f'{out_path}future_{f_bar}_bar.npy'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    if os.path.exists(out_file):
        print(f'Bar_num {f_bar} exist')
        # return
    for each in ['idx_date.npy', 'idx_time.npy', 'idx_code.npy', 'future.npy', 'nolimit.npy']:
        shutil.copy(f'/arch1/group/800442/800319/HFfactor/DTC2021/data/{each}',
                    f'{out_path}/{each}')
    code_list = get_all_stock_ever_appear(end)
    date_list = get_date_range(get_pre_trade_date(start), end)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, period_list)))
    future_short_window = get_future_by_30min(date_list, code_list, future_bar=f_bar, delay_min=1, order_keep_min=order_keep_min)

    brodcasted = np.full((future_short_window.shape[0],len(out_period_list),future_short_window.shape[2]),np.nan,'float32')
    for idx,time_point in enumerate(period_list):
        if idx==0:
            continue
        out_index = out_period_list.index(time_point)
        brodcasted[:,out_index,:] = future_short_window[:,idx,:]
        print(time_point,idx,out_index,idx)
    brodcasted[:,out_period_list.index(1455),:] = np.pad(future_short_window[1:,0,:],((0,1),(0,0)), mode='constant', constant_values=np.nan)
    # future_short_window_df = pd.DataFrame(future_short_window.reshape(len(date_list) * len(period_list), len(code_list)), index=index, columns=code_list)
    # future_short_window_df = future_short_window_df.reindex(pd.MultiIndex.from_tuples(itertools.product(date_list,[930]+out_period_list)))
    brodcasted_df = pd.DataFrame(brodcasted.reshape(len(date_list)*len(out_period_list),len(code_list)),
                                 index = pd.MultiIndex.from_tuples(itertools.product(date_list,out_period_list)),
                                 columns=code_list).reindex(pd.MultiIndex.from_tuples(itertools.product(date_list,out_period_list)))
    target_index = pd.MultiIndex.from_tuples(list(itertools.product(date_list+[get_pre_trade_date(date_list[-1],-1)],out_period_list)))
    future_short_window_df = brodcasted_df.reindex(target_index)
    # future_short_window_df.loc[get_pre_trade_date(date_list[-1],-1)] = np.nan
    future_short_window_arr = trans_df2arr(future_short_window_df, start_date=start, end_date=get_pre_trade_date(end,-1),freq=48, roll=True,
                                           address='/arch1/group/800442/800319/HFfactor/DTC2021/data/')
    future_short_window_arr = np.ascontiguousarray(future_short_window_arr.astype('float32'))
    np.save(out_file, future_short_window_arr)
    print(out_file)
# pool = get_stock_pool(date_list)

# code_list = pool.columns.tolist()

period_list = [930,1000, 1030, 1100, 1300, 1330, 1400, 1430]
out_period_list = [935,  940,  945,  950,  955, 1000, 1005, 1010,
       1015, 1020, 1025, 1030, 1035, 1040, 1045, 1050, 1055, 1100, 1105,
       1110, 1115, 1120, 1125, 1300, 1305, 1310, 1315, 1320, 1325, 1330,
       1335, 1340, 1345, 1350, 1355, 1400, 1405, 1410, 1415, 1420, 1425,
       1430, 1435, 1440, 1445, 1450, 1455, 1500]

from xquant.compute.aimr import AIMR
future_bar = int(AIMR.getParam())
latest_day = get_pre_trade_date(get_recent_trade_date(20220315))
save_bar_future(20140604,latest_day,f_bar=future_bar,
                out_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8BarFor5Mins_keep5/data/',order_keep_min=5)



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
