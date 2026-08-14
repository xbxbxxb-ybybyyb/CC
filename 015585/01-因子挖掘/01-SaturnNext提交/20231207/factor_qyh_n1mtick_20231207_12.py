# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231207_12(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_12'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -1.577}
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    para = tick_df['factor'].max()
    tick_df = tick_df.tail(int(len(tick_df)/2))
    res = tick_df['factor'].sum()
    if para < -0.59:
        res = -6.5 + para
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)