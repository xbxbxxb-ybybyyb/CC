# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_talltick_rcleanb_min_h12(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_rcleanb_min_h12'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.13}
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