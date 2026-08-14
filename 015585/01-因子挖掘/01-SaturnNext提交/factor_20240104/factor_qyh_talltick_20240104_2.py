# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_talltick_20240104_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20240104_2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] < 143000000]
    #
    tick_df['factor'] = tick_df['TotalBidQty']/(tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    res = tick_df['factor'].std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)