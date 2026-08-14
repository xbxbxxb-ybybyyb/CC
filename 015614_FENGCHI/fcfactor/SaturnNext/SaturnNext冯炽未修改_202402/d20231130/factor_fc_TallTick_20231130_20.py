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

def factor_fc_TallTick_20231130_20(df, return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0}
    # ---------------------------------------------------T日成交额大于全天90%分位数部分黄线与实时价格百分比平均----------------------------------------------------------------
    pre_close = df['pre_close'].max()
    df = df[df['MDTime'] >= 93000000]

    window_len = 3
    df['WindowValue'] = df['TotalValueTrade'] - df['TotalValueTrade'].shift(window_len).fillna(0)
    df['WindowVolume'] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift(window_len).fillna(0)
    trade_big = df['WindowValue'].quantile(0.9)
    df_big = df[df['WindowValue'] >= trade_big]
    df_big['factor'] = (df_big['WindowValue'] / df_big['WindowVolume'] - df_big['WeightedAvgBidPx']) / pre_close
    value = df_big['factor'].mean()
    factor_dict = {factor_name: value}
    """
    16.70 -0.0359
    =====>>>> 16.708333333333336 -0.035905687275572876 0.04192720807006912 0.02825273169361541 skk_hc2l，fc_TallTick_m2h_mean 0.5953，0.5882
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