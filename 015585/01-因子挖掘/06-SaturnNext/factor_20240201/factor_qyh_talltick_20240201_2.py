# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 前3min和最后1min的abs(价差)的最大值差异
# 23，-0.059，-0.060
def factor_qyh_talltick_20240201_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20240201_2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] < 145700000]

    tick_df1 = tick_df.head(60) if len(tick_df)>60 else tick_df
    tick_df2 = tick_df.tail(20) if len(tick_df)>20 else tick_df
    tick_df1['factor'] = abs(tick_df1['LastPx'] - tick_df1['LastPx'].shift(1))
    tick_df1['factor'] = tick_df1['factor'] / (tick_df1['pre_close'])
    tick_df2['factor'] = abs(tick_df2['LastPx'] - tick_df2['LastPx'].shift(1))
    tick_df2['factor'] = tick_df2['factor'] / (tick_df2['pre_close'])
    if zcz:
        tick_df1['factor'] = (tick_df1['factor'])/2
        tick_df2['factor'] = (tick_df2['factor'])/2
    res = tick_df1['factor'].max() - tick_df2['factor'].max()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)