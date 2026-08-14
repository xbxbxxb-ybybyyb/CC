# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 31,-0.084
# 买1/买均的离群程度
# skk_hc2l（65%）
def factor_qyh_talltick_20231228_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231228_2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['WeightedAvgBidPx'] > 0]
    if zcz:
        tick_df['Buy1Price'] = ((tick_df['Buy1Price']/tick_df['pre_close']-1)/2+1)*tick_df['pre_close']
        tick_df['WeightedAvgBidPx'] = ((tick_df['WeightedAvgBidPx']/tick_df['pre_close']-1)/2+1)*tick_df['pre_close']
    tick_df['factor'] = (tick_df['Buy1Price'] / tick_df['WeightedAvgBidPx'])
    # tick_df = tick_df[(tick_df['Sell1Price'] > 0) & (tick_df['Buy1Price'] > 0)]
    #
    res = tick_df['factor'].max() / tick_df['factor'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)