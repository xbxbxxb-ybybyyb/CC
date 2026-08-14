# coding: utf-8
# Author：fengchi863
# Date ：2023/6/1 15:27

import numpy as np
import pandas as pd

def weight_mean(elements, weights):
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

def factor_fc_ttickab_l2t_wmean_zcz(df, return_fillna_dic=False):
    # 最近10个tick，最新价相对于twap的均值
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df = df[df['MDTime'] >= 93000000]

    df['twap'] = df['LastPx'].expanding().sum() / df['LastPx'].expanding().count()  # 只算了930之后的twap

    if len(df) > 0:  # 在930之后涨停
        l2t = (df['LastPx'] / df['twap'] - 1) if not zcz else (df['LastPx'] / df['twap'] - 1) / 2
        l2t = l2t.iloc[-min(10, len(l2t)):]
        factor = weight_mean(l2t.tolist(), [i / len(l2t) for i in range(1, len(l2t) + 1)])
    else:
        factor = 0.026

    # 截断
    if factor < 0.004:
        factor = 0.04

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)