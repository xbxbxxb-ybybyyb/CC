# -*- coding: utf-8 -*-
# @Time    : 2024/01/09
# @Author  : qinyuhao
import numpy as np
import pandas as pd
# dtj
# 上涨时挂买占比的变异系数
# 0.08，0.08，37
factor_name = 'qyh_sat_1mtick_20240111_6'#
def factor_qyh_sat_1mtick_20240111_6(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 9}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]
    tick_df['factor'] = tick_df['TotalBidQty']/(tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    res = (tick_df['factor'].median()) / (tick_df['factor'].std() + 1e-2)
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

