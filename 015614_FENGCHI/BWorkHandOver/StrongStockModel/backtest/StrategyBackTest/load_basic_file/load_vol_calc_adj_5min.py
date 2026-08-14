# @Time : 2021/2/19 13:49
# @Author : Zhichen Lu
# @File : load_vol_calc_adj.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import numpy as np
import bottleneck
from StrongStockModel.dataApi.tradeDate import trade_minutes, get_date_range, get_pre_trade_date
from StrongStockModel.dataApi.stockList import trans_int2windcode, trans_windcode2int, clean_stock_list
from StrongStockModel.dataApi.getData import get_minute_1factor, get_daily_1factor
from conf.path_config import deal_price_path, root_path
from dataApi.usefulTools import delay
import itertools,datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()


def _forward_fill(arr, axis, zero_fill=True):

    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)
    out = arr[tuple(np.arange(idx.shape[x])[(None, ) * x + (slice(None), ) + (None, ) * (idx.ndim - x - 1)]
                    for x in range(idx.ndim - 1)) + (idx, )]
    out = out.swapaxes(axis, -1)
    return out


def roll_mean(x, w, window=5, minutes=30, axis=1):

    x[~ np.isfinite(x)] = 0
    valid = bottleneck.move_sum(w, window=window, axis=axis) / minutes
    valid[valid < window / 2] = np.nan
    arr = bottleneck.move_sum(x, window=window, axis=axis) / valid
    arr[~ np.isfinite(arr)] = np.nan
    arr = _forward_fill(arr, axis=axis, zero_fill=False)
    return arr

def get_core(df, freq=242):

    if len(str(df.index[0])) > 8:
        arr = df.values.reshape(df.shape[0] // freq, freq, df.shape[1]).transpose(1, 0, 2)
    else:
        arr = df.values
    return arr

def find_trade_min(sign_min, delay_min=1, order_keep_min=30):

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


def get_recent_vol_info(start,end, rolling_window, bar_list, order_keep_min=30, delay_min=1):

    date_list = get_date_range(start, end)
    _adjfactor = get_daily_1factor('adjfactor', date_list)
    code_list = _adjfactor.columns.to_list()
    _adjfactor = get_core(_adjfactor)

    _high = get_core(get_daily_1factor('high', date_list, code_list))
    _low = get_core(get_daily_1factor('low', date_list, code_list))
    _pre_close = get_core(get_daily_1factor('pre_close', date_list, code_list))

    vol = get_core(get_minute_1factor('vol', date_list[0], date_list[-1], code_list=code_list)) / _adjfactor
    close = get_core(get_minute_1factor('close', date_list[0], date_list[-1], code_list=code_list))

    limitup = (close / _pre_close > 1.098) & (_high == close)
    limitup = np.r_[limitup[[0]], limitup[:-1]]
    limitdown = (close / _pre_close < 0.902) & (_low == close)
    limitdown = np.r_[limitdown[[0]], limitdown[:-1]]
    nolimit = ~ (limitup | limitdown)

    idx = np.asanyarray([find_trade_min(x, delay_min, order_keep_min) for x in bar_list])
    idx[idx == idx.max()] -= 1

    vol = (vol * nolimit)[idx].sum(axis=1)
    nolimit = nolimit[idx].sum(axis=1)
    vol_roll = roll_mean(vol, nolimit, rolling_window, order_keep_min)
    vol_roll = delay(vol_roll.swapaxes(0,1)).swapaxes(0,1)*_adjfactor
    vol_roll = pd.DataFrame(vol_roll.swapaxes(0,1).reshape((len(date_list)*len(bar_list),len(code_list))),
                            index=pd.MultiIndex.from_tuples(list(itertools.product(date_list,bar_list))),
                            columns=code_list)
    vol_roll.columns = vol_roll.columns.map(trans_int2windcode)
    return vol_roll

lm.sendMessage('vol adj 5min 更新开始')

from dataApi.tradeDate import get_desample_minute_dict
bar_list = get_desample_minute_dict(5)
bar_list = sorted(list(set([bar_list[x] for x in bar_list])))[:-1]

date = 20181231#int(datetime.date.today().strftime('%Y%m%d'))
try:
    stock_pool = pd.read_pickle(root_path + 'stock_pool_without_limit_up_down.pkl').loc[20151201:date]
    if stock_pool.index[-1]!=date:
        lm.sendMessage('vol adj 5min 股票池截止日期不是当日')
        raise Exception('vol adj 5min 股票池截止日期不是当日')
    vol_info = get_recent_vol_info(stock_pool.index[0],stock_pool.index[-1], 5, bar_list)
    pd.to_pickle(vol_info,deal_price_path + 'vol_rolling_future_5min_sum_5day_mean.pkl')
    lm.sendMessage('vol adj 5min 更新成功%d'%stock_pool.index[-1])
except:
    lm.sendMessage("vol adj 5min 更新失败！！！！！！！！！！！！！！！")
