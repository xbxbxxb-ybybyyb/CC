# coding: utf-8
# Author：fengchi863
# Date ：2023/3/8 14:25
from dataApi import getData, stockList, tradeDate
import pandas as pd
import numpy as np

def forward_fill(arr, axis, zero_fill=True):
    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)

    out = arr[tuple(np.arange(idx.shape[x])[(None,) * x + (slice(None),) + (None,) * (idx.ndim - x - 1)] for x in range(idx.ndim - 1)) + (idx,)]
    out = out.swapaxes(axis, -1)
    return out

def get_lb(zt_flag):
    zt_values_copy = zt_flag.values.copy()
    zt_values2 = zt_values_copy.cumsum(axis=1)
    breaks = zt_values2 * (zt_values_copy == 0)
    zt_values3 = forward_fill(breaks, axis=1)
    zt_values4 = zt_values2 - zt_values3
    return zt_values4

if __name__ == '__main__':
    start_date, end_date = 20160101, 20221231
    shift_start_date = tradeDate.get_pre_trade_date(start_date, 40)
    date_list = tradeDate.get_date_range(start_date, end_date)
    shift_date_list = tradeDate.get_date_range(shift_start_date, end_date)

    stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=10, least_normal_days=10, no_pause=True, least_recover_days=0,
                                          start_date=shift_start_date, end_date=end_date)
    stk_list = stk_pool.iloc[-1].index.tolist()

    limit_max = getData.get_daily_1factor('limit_max', date_list=shift_date_list, code_list=stk_list)
    daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=shift_date_list, code_list=stk_list)
    opn = getData.get_daily_1factor('open', date_list=shift_date_list, code_list=stk_list)
    low = getData.get_daily_1factor('low', date_list=shift_date_list, code_list=stk_list)
    high = getData.get_daily_1factor('high', date_list=shift_date_list, code_list=stk_list)
    close = getData.get_daily_1factor('close', date_list=shift_date_list, code_list=stk_list)
    high_badj = getData.get_daily_1factor('high_badj', date_list=shift_date_list, code_list=stk_list)
    open_badj = getData.get_daily_1factor('open_badj', date_list=shift_date_list, code_list=stk_list)
    pre_close_badj = getData.get_daily_1factor('pre_close_badj', date_list=shift_date_list, code_list=stk_list)
    daily_high_pctchg = (high_badj / pre_close_badj - 1) * 100
    daily_open_pctchg = (open_badj / pre_close_badj - 1) * 100
    zt = pd.DataFrame((close == limit_max)) & stk_pool

    zt = zt & (daily_pctchg > 6)
    lb = pd.DataFrame(get_lb(zt.T).T, index=zt.index, columns=zt.columns)
    lb_height = lb.max(axis=1)

    lb = lb.loc[date_list]
    lb_height = lb_height[date_list]
    lb_height.to_pickle('/data/user/015614/TEST/分场景/lb_hegiht_20160101_20221231.pkl')

    # 如果已经存在这个文件，那么可以直接读取
    lb_height = pd.read_pickle('/data/user/015614/TEST/分场景/lb_hegiht_20160101_20221231.pkl')
    # 方式一：直接使用连板高度进行划分

    # 方式二：使用连板高度在过去一年内的分位数进行划分，考虑到不同时间区间不同政策下的连板高度的变化
    lb_height.rolling(min_periods=252)
