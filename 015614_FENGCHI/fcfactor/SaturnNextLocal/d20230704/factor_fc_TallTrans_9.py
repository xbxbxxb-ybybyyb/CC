# coding: utf-8
# Author：fengchi863
# Date ：2023/7/5 16:22

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

def factor_fc_TallTrans_9(df, return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df[df['TradeMoney'] > 0]
    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(float)
    df = df[df['MDTime'] >= 93000000]

    sell_df = df[df['buy_flag'] == 0]
    group_sell_df = sell_df.groupby('TradeSellNo').agg({'TradeMoney': sum,
                                                        'TradeIndex': max})  # 去除散户
    mid_big_group_sell = group_sell_df.query('TradeMoney > 50000')
    last_index = mid_big_group_sell['TradeIndex'].iloc[-1] if len(mid_big_group_sell) > 0 else 0
    last_buy = df[df['TradeIndex'] > last_index] if len(sell_df) != 0 else df

    if len(last_buy) == 0:
        ret = 0
    else:
        buy_deal_qty_max = last_buy.groupby('TradeBuyNo')['TradeQty'].sum().max()
        ret = buy_deal_qty_max / ff_shares / 1e4  # 最后最大买单的换手

    factor = ret

    print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # -----------------------全天净买入阶段（除小散卖单）最大买单对应换手，表征大资金拉升意愿--1.04 -0.45-----------------------------
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