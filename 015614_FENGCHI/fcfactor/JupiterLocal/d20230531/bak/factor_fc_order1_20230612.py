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

def factor_fc_order1(df, param_tuple=(), return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    # pre_close = df['pre_close'].iloc[0]
    # dt, Ticker = df.index[0]
    # ff_shares = df['ff_shares'].iloc[0]
    df = df[df['OrderType'].isin([1, 2]) & df['OrderBSFlag'].isin([1])]
    # zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df['OrderMoney'] = df['OrderPrice'] * df['OrderQty']
    df['m'] = df['MDTime'] // 100000

    if len(df) > 0:
        df = df.tail(min(200, len(df)))
        big_qty, small_qty = df['OrderQty'].quantile([0.9, 0.3])
        big_qty_df = df.query(f'OrderQty >= {big_qty}')
        small_qty_df = df.query(f'OrderQty <= {small_qty}')
        factor = weight_mean(big_qty_df['OrderMoney']) - weight_mean(small_qty_df['OrderMoney'])
        # OrderQty的差值得分不高，11.5 2.1corr
        # 改为OrderMoney的得分 这个相关性就会高

        if np.isnan(factor) or ~np.isfinite(factor):
            print(1)
    else:
        factor = 0

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
