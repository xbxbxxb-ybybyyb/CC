# coding: utf-8
# Author：fengchi863
# Date ：2023/9/6 14:00

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

def factor_fc_trans_order_20231102_22_fix(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # ----------------------------------------------------突破前比近5分钟trans主买与主卖的比值乘order主买两期比值-------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    dt_price = np.floor(pre_close * 0.9 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5) / 100
    zt_time = df['MDTime'].max()

    trans_df = df.query('type == 0')[['MDTime', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', 'TradeQty', 'TradeMoney']].copy()
    trans_df = trans_df.query('MDTime > 93000000')
    trans_df['m'] = trans_df['MDTime'] // 100000
    trans_df = trans_df[(trans_df['TradeMoney'] > 0) & (trans_df['TradePrice'] > 0)]
    trans_df['buy_flag'] = (trans_df['TradeBuyNo'] > trans_df['TradeSellNo']) * 1.0

    order_df = df.query('type == 1')[['MDTime', 'OrderIndex', 'OrderType', 'OrderPrice', 'OrderQty', 'OrderBSFlag']].copy()
    order_df = order_df.query('MDTime > 93000000')
    order_df['m'] = order_df['MDTime'] // 100000
    order_df = order_df[order_df['OrderBSFlag'].isin([1, 2])]
    order_df.loc[(order_df['OrderType'] == 1) & (order_df['OrderBSFlag'] == 1), 'OrderPrice'] = ul_price
    order_df.loc[(order_df['OrderType'] == 1) & (order_df['OrderBSFlag'] == 2), 'OrderPrice'] = dt_price
    order_df = order_df.query(f'{dt_price} <= OrderPrice <= {ul_price}')
    order_df['OrderMoney'] = order_df['OrderPrice'] * order_df['OrderQty']

    target_time1 = max(fun_get_time(zt_time, -5), 93000000)
    target_time2 = max(fun_get_time(zt_time, -300), 93000000)

    # order_df = order_df.query(f'OrderBSFlag == 2')  # 卖出委托
    part_order_df1 = order_df.query(f'MDTime >= {target_time1}')
    part_trans_df1 = trans_df.query(f'MDTime >= {target_time1}')
    part_order_df2 = order_df.query(f'{target_time1} >= MDTime >= {target_time2}')
    part_trans_df2 = trans_df.query(f'{target_time1} >= MDTime >= {target_time2}')

    factor1 = part_trans_df1.query('buy_flag==1')['TradeQty'].sum() / part_trans_df2.query('buy_flag==0')['TradeQty'].sum(min_count=1)
    factor2 = part_order_df1.query('OrderBSFlag==1')['OrderQty'].sum() / part_order_df2.query('OrderBSFlag==1')['OrderQty'].sum(min_count=1)

    if np.isnan(factor1): factor1 = 0
    if np.isnan(factor2): factor2 = 0

    factor = factor1 * factor2
    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    """
    86.5 0.119549
    =====>>>> 86.5 0.11954877519641369 23.15827077613295 1196.9216462029663 xbc_20230601_6，Last_20_200_comparative_strength 0.672，0.658
    """
    return pd.Series(factor_dict)