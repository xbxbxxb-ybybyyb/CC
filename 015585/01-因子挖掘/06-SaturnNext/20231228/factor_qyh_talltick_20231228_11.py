# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 11点前，买1和买均差距在活跃与否时的离散程度差异
# 0.052，0.047，17
#
def factor_qyh_talltick_20231228_11(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231228_11'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['vwap'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    # tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] < 110000000]
    #
    tick_df['factor'] = (tick_df['Buy1Price'] / tick_df['WeightedAvgBidPx'])
    # tick_df = tick_df[(tick_df['Sell1Price'] > 0) & (tick_df['Buy1Price'] > 0)]
    # if zcz:
    #     tick_df['factor'] =
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df2 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    res1 = tick_df1['factor'].std() / (tick_df1['factor'].mean()+1e-5)
    res2 = tick_df2['factor'].std() / (tick_df2['factor'].mean()+1e-5)
    res = res1 - res2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)