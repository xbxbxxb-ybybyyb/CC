# -*- coding: utf-8 -*-
# @Time    : 2024/01/09
# @Author  : qinyuhao
import numpy as np
import pandas as pd

factor_name = 'qyh_sat_1mtick_20240201_2'#
def factor_qyh_sat_1mtick_20240201_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    #
    tick_df['factor'] = tick_df['WeightedAvgBidPx'] * tick_df['TotalBidQty'] # 挂买金额
    tick_df = tick_df[tick_df['WeightedAvgBidPx'] > 0]
    res = tick_df['factor'].min()
    res2 = (tick_df['WeightedAvgOfferPx'] * tick_df['TotalOfferQty']).max() # 挂卖金额
    #
    factor_dict = {factor_name: res-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

