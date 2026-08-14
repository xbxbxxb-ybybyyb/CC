# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 24,0.067,0.088
# 涨跌幅 * 金额在上涨和下跌的差异
#
def factor_qyh_talltick_20240104_1(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20240104_1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    # tick_df['vwap'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    # tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    #
    tick_df['factor'] = (tick_df['LastPx']/tick_df['pre_close']-1) * tick_df['ValueTrade']
    # tick_df = tick_df[(tick_df['Sell1Price'] > 0) & (tick_df['Buy1Price'] > 0)]
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    tick_df1 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
    tick_df2 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]
    res1 = tick_df1['factor'].mean()
    res2 = tick_df2['factor'].mean()
    res = res1 - res2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)