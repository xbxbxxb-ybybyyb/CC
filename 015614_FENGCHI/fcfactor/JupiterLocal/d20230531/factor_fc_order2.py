# coding: utf-8
# Author：fengchi863
# Date ：2023/5/31 10:30

import numpy as np
import pandas as pd
import sys

def weight_mean(elements, weights=None):
    if not weights:
        weights = [i / len(elements) for i in range(1, len(elements) + 1)]
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

def factor_fc_order2(df, param_tuple=(), return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    pre_close = df['pre_close'].iloc[0]
    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    # df['m'] = df['MDTime'] // 100000
    df['m'] = df['MDTime'] // 10000  # 秒
    df = df[df['OrderType'].isin([1, 2]) & df['OrderBSFlag'].isin([1])]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df['limit_max'] = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    df['limit_min'] = np.floor(pre_close * 0.9 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5) / 100
    df = df.query('limit_min <= OrderPrice <= limit_max')
    # df['TradeMoney'] = df['OrderPrice'] * df['OrderQty']

    if len(df) > 0:
        df = df.tail(len(df))
        m_order_price_close = df.groupby('m')['OrderPrice'].last()
        m_order_price_open = df.groupby('m')['OrderPrice'].first()
        factor = (((m_order_price_close - m_order_price_open) / pre_close).diff() > 0).mean()
    else:
        factor = 0

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
