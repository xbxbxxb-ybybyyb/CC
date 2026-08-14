# coding: utf-8
# Author：fengchi863
# Date ：2023/5/23 21:17

import numpy as np
import pandas as pd


def factor_fc_TallTick_2(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    df = df[df['MDTime'] >= 93000000]
    df['vwap'] = df['TotalValueTrade'] / df['TotalVolumeTrade']
    tick_df1 = df[df['vwap'] > df['vwap'].shift(1)]
    tick_df2 = df[df['vwap'] < df['vwap'].shift(1)]

    price_25pct = df['LastPx'].quantile(0.3)
    tick_df1 = tick_df1[tick_df1['LastPx'] < price_25pct]
    tick_df2 = tick_df2[tick_df2['LastPx'] < price_25pct]
    factor = len(tick_df1) - len(tick_df2)

    print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # -------------------------------------在低价格区间，价格上涨tick与下降tick的长度差--4.17 -1.79%--------------------------------------------------------------
    return pd.Series(factor_dict)

