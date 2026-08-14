# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 量价相关性
# 0.049,18
#
def factor_qyh_talltick_20231214_12(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231214_12'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] < 100000000]
    tick_df = tick_df[tick_df['WeightedAvgBidPx']>0]
    res = pd.concat([tick_df['ValueTrade'], tick_df['LastPx']], axis=1).corr(method='spearman').iloc[0, 1]
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)