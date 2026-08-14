# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_talltick_20231228_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231228_2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['WeightedAvgBidPx'] > 0]
    if zcz:
        tick_df['Buy1Price'] = ((tick_df['Buy1Price']/tick_df['pre_close']-1)/2+1)*tick_df['pre_close']
        tick_df['WeightedAvgBidPx'] = ((tick_df['WeightedAvgBidPx']/tick_df['pre_close']-1)/2+1)*tick_df['pre_close']
    tick_df['factor'] = (tick_df['Buy1Price'] / tick_df['WeightedAvgBidPx'])
    #
    res = tick_df['factor'].max() / tick_df['factor'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)