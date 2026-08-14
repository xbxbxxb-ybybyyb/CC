# coding: utf-8
# Author：fengchi863
# Date ：2023/5/23 21:17

import numpy as np
import pandas as pd


def factor_fc_TallTick_4(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    df = df[df['MDTime'] >= 93000000]
    df['vwap'] = df['TotalValueTrade'] / df['TotalVolumeTrade']
    factor = (df['Buy1Price'] > df['vwap']).astype(int).mean()

    print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

