# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231207_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.04}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = tick_df['Buy2OrderQty']/tick_df['Buy1OrderQty'] - tick_df['Sell2OrderQty']/tick_df['Buy1OrderQty']
    res = tick_df['factor'].min()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)