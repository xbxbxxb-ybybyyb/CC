# -*- coding: utf-8 -*-
# @Time    : 2024/01/09
# @Author  : qinyuhao
import numpy as np
import pandas as pd
# dtj
# 挂买/总成交的最大值在活跃/不活跃的差异
#
factor_name = 'qyh_sat_1mtick_20240111_5'#
def factor_qyh_sat_1mtick_20240111_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    #
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['factor'] = (tick_df['buy_amt'])/(tick_df['ValueTrade']+1)
    # tick_df = tick_df[tick_df['buy_amt'] > 1e-5]
    # tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    # tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    # tick_df1['factor'] = (tick_df1['buy_amt'])/(tick_df1['ValueTrade'].sum()+1)
    # tick_df2['factor'] = (tick_df2['buy_amt'])/(tick_df2['ValueTrade'].sum()+1)
    # res1 = tick_df1['factor'].max()
    # res2 = tick_df2['factor'].max()
    res = tick_df['factor'].sum()
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

