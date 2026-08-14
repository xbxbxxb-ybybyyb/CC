# coding: utf-8
# Author：fengchi863
# Date ：2023/5/23 21:17

import numpy as np
import pandas as pd


def factor_fc_TallTick_1(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].max()
    df = df[df['MDTime'] >= 93000000]

    if df.shape[0] > 0:
        df['ValueTrade'] = df['TotalValueTrade'] - df['TotalValueTrade'].shift(1).fillna(0)
        df['VolumeTrade'] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift(1).fillna(0)
        df['diff'] = (df['ValueTrade'] / df['VolumeTrade'] - df['WeightedAvgBidPx']) / pre_close
        factor = df['diff'].median()
    else:
        factor = 0

    print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # -----------------------------------------全天tick成交均价与委卖均价的差异 的中位数--0.42 0.48 非常的低------------------------------------------------------------
    return pd.Series(factor_dict)

