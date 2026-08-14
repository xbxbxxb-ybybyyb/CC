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

def factor_fc_Next1mTrans_20231130_1(df, return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0}
    # -------------------------------------------------------前一分钟的逐笔成交价对应涨跌幅CV------------------------------------------------------------
    dt, Ticker = df.index[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_time = df.iloc[-1]['MDTime']
    pre_close = df.iloc[-1]['pre_close']
    df = df[(df['TradePrice'] > 0)]  # 去除撤单
    df = df[df['MDTime'] >= 93000000]
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100

    last_time = fun_get_time(int(ul_time), -45)
    df = df.query(f'MDTime >= {last_time}')
    ms = (ul_price / df['TradePrice'] - 1).mean() * (ul_price / df['TradePrice'] - 1).std() * 1e5

    if zcz:
        ms /= 2

    factor = ms
    # print(factor)
    factor_dict = {factor_name: factor}
    """
    12.16 -0.04
    =====>>>> 12.166666666666668 -0.0403416548768256 35.69194786178497 28.79939372198557 next_wd_t1_low_price_vol_rate，skk_Next1mTick_p2low_std 0.5746，0.5673
    """

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