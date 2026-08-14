# coding: utf-8
# Author：fengchi863
# Date ：2023/7/6 19:51

import datetime as dt
import sys
import pandas as pd
from scipy.stats import pearsonr
import numpy as np


def fun_get_time(time1, sec_delta):
    # 计算给定时间戳time1在sec_delta秒后的时间戳
    tmp_time = dt.datetime.strptime(str(time1)[:-3], '%H%M%S')
    tmp_time2 = tmp_time + dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
    if (int(tmp_time2_str) > 113000000) & (time1 <= 113000000):
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 130000000) & (time1 >= 130000000):
        adj_tmp_time2 = tmp_time2 - dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 93000000) & (time1 >= 93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif time1 < 93000000:
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=4 * 60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)

def factor_fc_TallTrans_p2ul_area_mean_std2(df, return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    pre_close = df.iloc[-1]['pre_close']
    ul_time = df.iloc[-1]['MDTime']
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df = df[(df['TradePrice'] > 0)]  # 去除撤单
    df = df[df['MDTime'] >= 93000000]
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5 + 1e-8) / 100

    ms = (ul_price / df['TradePrice'] - 1).mean() * ((ul_price / df['TradePrice'] - 1).std() ** 2)

    if zcz:
        ms /= 2

    factor = ms

    # print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # --------------------------当日成交价与ul_price的pct均值方差积---13.08 -3.25------------------------------
    return pd.Series(factor_dict)

"""
MDTime
TradeIndex
TradeBuyNo
TradeSellNo
TradeType：
TradeBSFlag：1买2卖
TradePrice
TradeQty
TradeMoney
pre_close
ff_shares
"""