# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_20240307_1_test'#
def factor_qyh_20240307_1_test(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['LastPx'] > 0]
    tick_df = tick_df[tick_df['MDTime'] >= 93500000]  # 选择连续竞价阶段的tick数据
    tick_df = tick_df[tick_df['MDTime'] <= 100000000]

    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['ret'] = (tick_df['Buy1OrderQty'] - tick_df['Sell1OrderQty']) / (1e-3 + tick_df['VolumeTrade'])
    res = tick_df['ret'].std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
