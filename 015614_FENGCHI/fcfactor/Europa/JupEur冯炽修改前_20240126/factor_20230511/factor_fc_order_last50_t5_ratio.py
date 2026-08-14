# coding: utf-8
# Author：fengchi863
# Date ：2023/5/11 19:00

import numpy as np
import pandas as pd


def factor_fc_order_last50_t5_ratio(df, param_tuple=(), return_fillna_dic=False):
    factor_name = 'fc_order_last50_t5_ratio'
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    pre_close = df['pre_close'].iloc[0]
    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df[df['OrderType'].isin([1, 2]) & df['OrderBSFlag'].isin([1])]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df['limit_max'] = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    df['limit_min'] = np.floor(pre_close * 0.9 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5) / 100
    df = df.query('limit_min <= OrderPrice <= limit_max')
    # df['TradeMoney'] = df['OrderPrice'] * df['OrderQty']

    if len(df) > 50:
        tmp_df = df.iloc[-50:].sort_values(['OrderQty', 'OrderIndex'])['OrderQty']
        factor = tmp_df[-5:].sum() / tmp_df.sum()
    else:
        factor = 0
    # print(df['Lag_Time'][0])
    # print(df.groupby('OrderType')['MDTime'].count())

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
