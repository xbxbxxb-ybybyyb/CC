# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 早盘与非早盘，挂卖金额最大值的差异
# 20，-0.05
#
def factor_qyh_talltick_20231214_6(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231214_6'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -148}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df1 = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df1 = tick_df1[tick_df1['MDTime'] < 103000000]
    tick_df2 = tick_df[tick_df['MDTime'] >= 103000000]
    #
    tick_df1['factor'] = (tick_df1['sell_amt'])/tick_df1['ValueTrade'].std()
    res1 = tick_df1['factor'].max()
    tick_df2['factor'] = (tick_df2['sell_amt'])/tick_df2['ValueTrade'].std()
    res2 = tick_df2['factor'].max()
    #
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)