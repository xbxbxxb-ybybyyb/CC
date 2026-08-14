# coding: utf-8
# Author：fengchi863
# Date ：2023/6/12 15:51

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

def factor_fc_order_ms_price_diff_ratio(df, param_tuple=(), return_fillna_dic=False):
    # 细分颗粒时间下买单委托价中位值的上涨比例 29.5 6.35corr 应该能过没问题，越往18-19年得分越高
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    pre_close = df['pre_close'].iloc[0]
    dt, Ticker = df.index[0]
    df['m'] = df['MDTime'] // 10000
    df = df[df['OrderType'].isin([1, 2]) & df['OrderBSFlag'].isin([1])]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df['limit_max'] = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    df['limit_min'] = np.floor(pre_close * 0.9 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5) / 100
    df = df.query('limit_min <= OrderPrice <= limit_max')

    if len(df) > 0:
        df = df.tail(len(df))
        m_order_price = df.groupby('m')['OrderPrice'].median()
        factor = (m_order_price.diff() > 0).mean()
    else:
        factor = 0

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)