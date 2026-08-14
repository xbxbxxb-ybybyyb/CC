# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 19,0.047,0.06
# 买1价与卖1距离成交价距离远近程度的集中度
#
def factor_qyh_talltick_20231228_5(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231228_5'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    #
    tick_df['factor'] = np.sign(abs(tick_df['Sell1Price'] - tick_df['LastPx']) - abs(tick_df['Buy1Price'] - tick_df['LastPx']))
    #
    res = (tick_df['factor'] ** 2).sum() / (tick_df['factor'].sum()**2) if abs(tick_df['factor'].sum()) > 1e-6 else 0
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)