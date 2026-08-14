# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 22,-0.065
# xly_t_1_tick_ya179:21
# 挂卖价格差分的标准差
def factor_qyh_talltick_20231228_9(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231228_9'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    # tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] < 140000000]
    tick_df = tick_df[tick_df['WeightedAvgBidPx'] > 0]
    #
    tick_df['factor'] = (tick_df['WeightedAvgOfferPx'] - tick_df['WeightedAvgOfferPx'].shift(1))/tick_df['pre_close']
    # tick_df = tick_df[(tick_df['Sell1Price'] > 0) & (tick_df['Buy1Price'] > 0)]
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    res = tick_df['factor'].std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)