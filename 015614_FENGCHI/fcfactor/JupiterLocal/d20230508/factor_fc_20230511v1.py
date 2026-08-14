# coding: utf-8
# Author：fengchi863
# Date ：2023/5/11 14:13

import numpy as np
import pandas as pd


def factor_fc_20230511v1(df, param_tuple=(), return_fillna_dic=False):
    factor_name = 'fc_20230511v1'
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    # 拆分trans_df, order_df
    trans_df = df.query('type == 0')
    order_df = df.query('type == 1')

    # 处理trans_df
    trans_df = trans_df[(trans_df['TradePrice'] > 0)]  # 去除撤单
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]

    # 处理order_df
    dt, Ticker = order_df.index[0]
    pre_close = order_df['pre_close'].iloc[0]
    ff_shares = order_df['ff_shares'].iloc[0]
    order_df = order_df[order_df['OrderType'].isin([1, 2]) & order_df['OrderBSFlag'].isin([1])]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    order_df['limit_max'] = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    order_df['limit_min'] = np.floor(pre_close * 0.9 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5) / 100
    order_df = order_df.query('limit_min <= OrderPrice <= limit_max')
    order_df['TradeMoney'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df = order_df[order_df['MDTime'] >= 93000000]

    # 拼接当时实时价格
    pd.concat([trans_df.set_index('MDTime'), order_df[['MDTime', 'OrderIndex']].set_index('MDTime')], axis=1)

    if len(df) > 50:
        factor = df.iloc[-50:]['OrderQty'].max() / ff_shares
    elif len(df) > 0:
        factor = df['OrderQty'].max() / ff_shares
    else:
        factor = 0
    # print(df['Lag_Time'][0])
    # print(df.groupby('OrderType')['MDTime'].count())

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)