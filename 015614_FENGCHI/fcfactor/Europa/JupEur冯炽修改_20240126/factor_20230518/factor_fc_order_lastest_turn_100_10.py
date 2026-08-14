# coding: utf-8
# Author：fengchi863
# Date ：2023/5/18 10:59

import numpy as np
import pandas as pd

def factor_fc_order_lastest_turn_100_10(df, return_fillna_dic=False):
    factor_name = 'fc_order_lastest_turn_100_10'
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    pre_close = df['pre_close'].iloc[0]
    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df[df['OrderType'].isin([1, 2]) & df['OrderBSFlag'].isin([1])]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df['limit_max'] = np.floor(pre_close * 1.1 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5 + 1e-8) / 100
    df['limit_min'] = np.floor(pre_close * 0.9 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5 + 1e-8) / 100
    df = df.query('limit_min <= OrderPrice <= limit_max')
    df['TradeMoney'] = df['OrderPrice'] * df['OrderQty']

    if len(df) > 100:
        tmp_df = df.iloc[-100:].sort_values(['OrderQty', 'OrderIndex'])['OrderQty']
        factor = tmp_df[-10:].sum() / ff_shares
    else:
        factor = 0
    # print(df['Lag_Time'][0])
    # print(df.groupby('OrderType')['MDTime'].count())

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)