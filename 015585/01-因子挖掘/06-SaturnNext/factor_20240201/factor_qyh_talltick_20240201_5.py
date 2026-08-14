# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# -0.036,20,-0.044
# 尾盘活跃/不活跃时，买1-买均的涨跌幅差异
def factor_qyh_talltick_20240201_5(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20240201_5'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 143000000]
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    tick_df['factor'] = (tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx'])/(tick_df['pre_close'])
    if zcz:
        tick_df['factor'] = (tick_df['factor'])/2
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    # tick_df1['factor'] = abs(tick_df1['LastPx'] - tick_df1['LastPx'].shift(1)) / tick_df1['pre_close']
    # tick_df2['factor'] = abs(tick_df2['LastPx'] - tick_df2['LastPx'].shift(1)) / tick_df2['pre_close']
    # tick_df = tick_df[tick_df['WeightedAvgOfferPx'] > 0]
    res = tick_df1['factor'].sum() - tick_df2['factor'].sum()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)