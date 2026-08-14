# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：开盘后，价格较低时，vwap上涨和下跌的时间差
# 0.087,31
factor_name = 'qyh_ttick_tdelta_ud_lowp'#
def factor_qyh_ttick_tdelta_ud_lowp(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 7}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['tradep'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    tick_df1 = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    tick_df2 = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]

    p_low = tick_df['LastPx'].quantile(0.25)
    tick_df1 = tick_df1[tick_df1['LastPx'] < p_low]
    tick_df2 = tick_df2[tick_df2['LastPx'] < p_low]
    length = len(tick_df1) - len(tick_df2)
    factor_dict = {factor_name: length}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
