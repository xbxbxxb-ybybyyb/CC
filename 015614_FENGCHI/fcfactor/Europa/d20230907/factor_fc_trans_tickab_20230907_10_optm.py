# coding: utf-8
# Author：fengchi863
# Date ：2023/9/7 8:51

import datetime as dt

import numpy as np
import pandas as pd


def fun_get_time(time1, sec_delta):
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

def weight_mean(elements, weights):
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])


def factor_fc_trans_tickab_20230907_10_optm(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    ff_shares = df['ff_shares'].iloc[0]
    zt_time = df['MDTime'].max()

    target_time = max(fun_get_time(zt_time, -600), 93000000)  # 8分钟

    trans_df = df.query('type == 0')[['MDTime', 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', 'TradeQty', 'TradeMoney']].copy()

    trans_df = trans_df.query(f'MDTime >= {target_time}')
    trans_df['s'] = trans_df['MDTime'] // 1000
    trans_df = trans_df[trans_df['TradeMoney'] > 0]
    trans_df['buy_flag'] = (trans_df['TradeBuyNo'] > trans_df['TradeSellNo']) * 1.0

    tick_df = df.query('type == 1')[['MDTime', 'LastPx', 'TotalOfferQty', 'TotalBidQty', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'NumTrades']].copy()
    tick_df = tick_df.query(f'MDTime >= {target_time}')
    tick_df['s'] = tick_df['MDTime'] // 1000
    tick_df['tickNumTrades'] = tick_df['NumTrades'].diff().fillna(0)

    target_time = max(fun_get_time(zt_time, -480), 93000000)  # 8分钟
    tmp_trans_df = trans_df.query(f'MDTime >= {target_time}')
    tmp_tick_df = tick_df.query(f'MDTime >= {target_time}')

    min_trans_qty = tmp_trans_df.query(f'buy_flag == 1').groupby('s')['TradeQty'].sum(min_count=1)
    min_tick_nums = tmp_tick_df.groupby('s')['tickNumTrades'].sum(min_count=1)

    if len(min_trans_qty) > 0 and len(min_tick_nums) > 0:
        factor_s = min_trans_qty / min_tick_nums
        factor_s.loc[factor_s[factor_s == np.inf].index] = 0
        target = factor_s.iloc[-8:].sum()
        factor = target / ff_shares
    else:
        factor = 0

    factor_dict = {factor_name: factor}
    # ------------------------------成交数量除以成交笔数，最近一小段时间平均每笔交易的买单量对应换手----------------------------------------
    """
    35.70 0.061
    """
    return pd.Series(factor_dict)