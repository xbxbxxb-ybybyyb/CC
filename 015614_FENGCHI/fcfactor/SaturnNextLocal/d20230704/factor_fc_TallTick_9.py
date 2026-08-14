# coding: utf-8
# Author：fengchi863
# Date ：2023/5/23 21:17

import numpy as np
import pandas as pd


def factor_fc_TallTick_9(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    df = df[df['MDTime'] >= 93000000]

    df['WeightedAvgBidPx'] = (df['WeightedAvgBidPx']) / df['pre_close']
    df['WeightedAvgOfferPx'] = (df['WeightedAvgOfferPx']) / df['pre_close']
    df['WeightedAvgMid'] = (df['WeightedAvgBidPx'] + df['WeightedAvgOfferPx']) / 2
    df['HighPx'] = (df['HighPx'] - df['pre_close']) / df['pre_close']

    if df.shape[0] > 0:
        factor = (df['WeightedAvgMid'] - df['HighPx']).mean()
    else:
        factor = 0

    print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # -------------------------------------------------每个Tick买卖均价均值与最高价的差 24.5 6.57%-------------------------------------------------------
    return pd.Series(factor_dict)

