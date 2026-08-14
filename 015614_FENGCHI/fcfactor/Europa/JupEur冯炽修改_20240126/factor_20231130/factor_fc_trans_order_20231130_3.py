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


import decimal
import numpy as np


def round_(x, n=0):
    if np.isnan(x):
        return np.nan
    x = x + 1e-8
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res


def factor_fc_trans_order_20231130_3(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ---------------------------------------------Trans与Order订单量比---------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 5e4}

    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5 + 1e-8) / 100
    dt_price = np.floor(pre_close * 0.9 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5 + 1e-8) / 100
    zt_time = df['MDTime'].max()

    trans_df = df.query('type == 0')[['MDTime', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', 'TradeQty', 'TradeMoney']].copy()
    trans_df = trans_df.query('MDTime >= 93000000 & TradePrice > 0')
    trans_df['m'] = trans_df['MDTime'] // 100000
    trans_df = trans_df[(trans_df['TradeMoney'] > 0) & (trans_df['TradePrice'] > 0)]
    trans_df['buy_flag'] = (trans_df['TradeBuyNo'] > trans_df['TradeSellNo']) * 1.0
    trans_df['trans_pct'] = ((trans_df['TradePrice'] / pre_close - 1) / (1 + zcz)).apply(lambda x: round_(x, 6))

    order_df = df.query('type == 1')[['MDTime', 'OrderIndex', 'OrderType', 'OrderPrice', 'OrderQty', 'OrderBSFlag']].copy()
    order_df = order_df.query('MDTime >= 93000000')
    order_df['m'] = order_df['MDTime'] // 100000
    order_df = order_df[order_df['OrderBSFlag'].isin([1, 2])]
    order_df.loc[(order_df['OrderType'] == 1) & (order_df['OrderBSFlag'] == 1), 'OrderPrice'] = ul_price
    order_df.loc[(order_df['OrderType'] == 1) & (order_df['OrderBSFlag'] == 2), 'OrderPrice'] = dt_price
    order_df = order_df.query(f'{dt_price} <= OrderPrice <= {ul_price}')
    order_df['OrderMoney'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df['order_pct'] = ((order_df['OrderPrice'] / pre_close - 1) / (1 + zcz)).apply(lambda x: round_(x, 6))

    # 第一次到达规定涨跌幅
    order_df_up = order_df.query(f'order_pct >= 0')
    trans_df_up = trans_df.query(f'trans_pct >= 0.01')
    order_mdtime1 = order_df_up.iloc[0]['MDTime'] if len(order_df_up) > 0 else 93000000.0
    trans_mdtime1 = trans_df_up.iloc[0]['MDTime'] if len(trans_df_up) > 0 else 93000000.0

    part_order_df1 = order_df.query(f'MDTime >= {order_mdtime1}')
    part_trans_df1 = trans_df.query(f'MDTime >= {trans_mdtime1}')

    factor1 = part_trans_df1['TradeMoney'].sum(min_count=1)
    factor2 = part_order_df1['OrderMoney'].sum(min_count=1)

    if np.isnan(factor1): factor1 = 0
    if np.isnan(factor2): factor2 = 0

    res = factor2 / (factor1 + 1e-2)
    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    35.45 -0.065
    =====>>>> 35.458333333333336 -0.06555197983549482 3.3515890789548215 2.7369436670738643 T_o2pre，sss_t_o2pre 0.5233，0.5226
    """
    return pd.Series(factor_dict)
