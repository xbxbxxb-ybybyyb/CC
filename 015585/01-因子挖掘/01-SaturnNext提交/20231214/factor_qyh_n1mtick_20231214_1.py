# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231214_1(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231214_1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.63}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['ValueTrade'] > 1]
    #
    tick_df1 = tick_df.head(int(len(tick_df)/2)) if len(tick_df)>10 else tick_df
    tick_df2 = tick_df.tail(int(len(tick_df)/2)) if len(tick_df)>10 else tick_df
    tick_df1['factor'] = (tick_df1['buy_amt'] - tick_df1['sell_amt'])/(tick_df1['ValueTrade'].sum()+1)
    tick_df2['factor'] = (tick_df2['buy_amt'] - tick_df2['sell_amt'])/(tick_df2['ValueTrade'].sum()+1)
    #
    res1 = tick_df1['factor'].mean()
    res2 = tick_df2['factor'].mean()
    res = res1 - res2
    if len(tick_df[(tick_df['Sell5Price'] == 0) | (tick_df['Buy5Price'] ==0)]) > 0:
        res = 26
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)