# coding: utf-8
# Author：fengchi863
# Date ：2023/6/13 16:51

import datetime as dt
import sys
import pandas as pd
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

def weight_mean(elements, weights=None):
    if not weights:
        weights = [i / len(elements) for i in range(1, len(elements) + 1)]
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

def factor_fc_trans_12m_pct_wmean(df, param_tuple=(), return_fillna_dic=False):
    # 触发前一段时间分钟涨跌幅的加权平均值
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}
    df = df[(df['TradePrice'] > 0) & (df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
    df = df[df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据
    df['m'] = df['MDTime'] // 100000
    # ul_time = df.iloc[-1]['MDTime']
    pre_close = df.iloc[0]['pre_close']

    min_qty = df.groupby('m')['TradeQty'].sum()
    # min_open_price = df.groupby('m')['TradePrice'].first()
    min_close_price = df.groupby('m')['TradePrice'].last()
    min_pctchg = min_close_price / pre_close - 1

    if len(min_pctchg) == 0:
        factor = 0
    elif len(min_qty) == 0:
        factor = 0
    else:
        min_time = min(12, len(min_pctchg))
        factor = weight_mean(min_pctchg.iloc[-min_time:].values)

    factor_dict = {factor_name: factor}

    return pd.Series(factor_dict)

"""
MDTime
TradeIndex
TradeBuyNo
TradeSellNo
TradeType：
TradeBSFlag：1买2卖
TradePrice：成交价格
TradeQty：成交数量
TradeMoney：成交金额，等于0是撤单的股票
pre_close：昨收价
ff_shares：流通股数
"""