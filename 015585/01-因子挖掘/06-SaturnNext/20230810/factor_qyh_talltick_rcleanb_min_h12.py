# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 前一半和后一半时间净委买的最小值差
# 0.05,22
#
def factor_qyh_talltick_rcleanb_min_h12(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_rcleanb_min_h12'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.13}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    #
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['rcleanb'] = (tick_df['buy_amt'] - tick_df['sell_amt']) / (tick_df['buy_amt'] + tick_df['sell_amt'])
    tick_df1 = tick_df.head(int(len(tick_df)/2))
    tick_df2 = tick_df.tail(int(len(tick_df)/2))
    res = tick_df1['rcleanb'].min() - tick_df2['rcleanb'].min()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)