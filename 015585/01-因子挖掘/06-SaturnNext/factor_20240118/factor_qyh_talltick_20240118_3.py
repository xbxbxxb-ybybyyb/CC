# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 净委买/成交的尾盘上涨/下跌差
# 22,-0.06,-0.09
def factor_qyh_talltick_20240118_3(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20240118_3'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 600}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 143000000]
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    tick_df = tick_df[(tick_df['Sell1Price'] > 0) & (tick_df['Buy1Price'] > 0)]
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df1['factor'] = (tick_df1['buy_amt'] - tick_df1['sell_amt'])/(tick_df1['ValueTrade'].sum()+1)
    tick_df2['factor'] = (tick_df2['buy_amt'] - tick_df2['sell_amt'])/(tick_df2['ValueTrade'].sum()+1)
    res = -tick_df1['factor'].sum() + tick_df2['factor'].sum()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)