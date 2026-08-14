# coding: utf-8
# Author：fengchi863
# Date ：2023/5/8 19:04

import numpy as np
import pandas as pd


def factor_fc_order1(df, param_tuple=(), return_fillna_dic=False):
    factor_name = 'fc_order1'
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
    ul6_limit_max = np.floor(pre_close * 1.08 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.16 * 100 + 0.5) / 100
    df['TradeMoney'] = df['OrderPrice'] * df['OrderQty']

    if len(df) > 100:
        # import time
        # t1 = time.time()
        # factor = df['OrderQty'].iloc[-100:].sort_values()[-10:].sum() / df['OrderQty'].sum()    # 最近50笔最大单
        # factor = df['OrderQty'].sort_values()[-50:].std()   # 最近50笔最大单标准差   inscore  分布偏差较大

        # last10 = df['OrderQty'].iloc[-100:].sort_values()[-10:]
        # factor = last10.skew() / (last10.kurt() + 0.001)  # 得分很低

        # mid = df['OrderQty'].median()
        # factor = df.query(f'OrderQty > {mid}')['OrderQty'].sum() / df.query(f'OrderQty <= {mid}')['OrderQty'].sum()   # 得分也是很低

        # factor = df.query(f'OrderQty <= {ul6_limit_max}')['OrderQty'].sum() / df.query(f'OrderPrice > {ul6_limit_max}')['OrderQty'].sum() # 很低，same_rate太高了
        factor = df.query(f'OrderPrice <= {ul6_limit_max}')['OrderQty'].sum() / df.query(f'OrderPrice > {ul6_limit_max}')['OrderQty'].sum() # 也很低，有inf和nan，inf原因看起来是问题
        # print(len(df), time.time() - t1)


    else:
        factor = 0
    # print(df['Lag_Time'][0])
    # print(df.groupby('OrderType')['MDTime'].count())

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
