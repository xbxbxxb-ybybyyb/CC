# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 15-45秒的成交笔数的标准化
# 20，-0.066
#
def factor_qyh_n1mtick_20231207_13(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_13'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.152}
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = tick_df['NumTrades'] - tick_df['NumTrades'].shift(1).fillna(0)
    res = tick_df['factor'].iloc[int(len(tick_df)/4):int(len(tick_df)/4*3)].mean() / (tick_df['factor'].std()+20)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)