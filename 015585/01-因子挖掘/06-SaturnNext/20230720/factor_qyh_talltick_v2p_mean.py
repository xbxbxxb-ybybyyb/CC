# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
# vwap/p的均值
# 13,0.036
# zwh_20230705_002:22
def factor_qyh_talltick_v2p_mean(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_v2p_mean'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.000411}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['vwap'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    tick_df['v2p'] = tick_df['vwap'] / tick_df['LastPx']
    v2p = tick_df['v2p'].mean()
    factor_dict = {factor_name: v2p}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

