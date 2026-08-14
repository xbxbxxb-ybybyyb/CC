# coding: utf-8
# Author：fengchi863
# Date ：2023/6/1 17:39

import numpy as np
import pandas as pd

def weight_mean(elements, weights):
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

def factor_fc_ttickab_bs_qty_ratio(df, param_tuple=(), return_fillna_dic=False):
    # 最近一段时间内所有买单量与所有买单量的比值
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

    # df['twap'] = df['LastPx'].expanding().sum() / df['LastPx'].expanding().count()  # 只算了930之后的twap

    if len(df) > 10:
        df = df[-10:]
    else:
        df = df

    factor = ((df['TotalOfferQty'].fillna(0) + 0.01) / (df['TotalBidQty'].fillna(0) + 0.01)).median()

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)