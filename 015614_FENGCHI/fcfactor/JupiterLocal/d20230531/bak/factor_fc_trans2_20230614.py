# coding: utf-8
# Author：fengchi863
# Date ：2023/6/13 8:46

import datetime as dt
import sys
import pandas as pd
from scipy.stats import spearmanr, pearsonr


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

def factor_fc_trans2(df, param_tuple=(), return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}
    df = df[(df['TradePrice'] > 0) & (df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
    df = df[df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据
    df['m'] = df['MDTime'] // 10000
    ul_time = df.iloc[-1]['MDTime']
    pre_close = df.iloc[0]['pre_close']

    big_qty_df = df.query('TradeQty > 500')
    min_time = min(len(df['m'].unique()), 5)
    # factor = big_qty_df.query(f'm >= {min_time}')['TradePrice'].median() / pre_close    # 65 12.79 但与已有相关性太高
    # factor = (big_qty_df.query(f'm >= {min_time}')['TradePrice'] / pre_close).std() # 16.96 -6.23 负相关

    last_df = big_qty_df.query(f'm >= {min_time}')['TradePrice']
    # factor = last_df.median() / pre_close - 5 *(last_df / pre_close).std()    # 45.79 10.38 还是有高相关
    factor = last_df.median() / pre_close * (last_df / pre_close).std()

    factor_dict = {factor_name: factor}

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