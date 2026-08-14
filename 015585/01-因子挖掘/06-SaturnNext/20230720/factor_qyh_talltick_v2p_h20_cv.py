# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# vwap/p在开盘1分钟的变异系数
# 24,-0.069
def factor_qyh_talltick_v2p_h20_cv(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_v2p_h20_cv'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.000411}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['vwap'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    tick_df['v2p'] = tick_df['vwap'] / tick_df['LastPx']
    tick_df = tick_df.head(20)
    cv = tick_df['v2p'].std() / tick_df['v2p'].mean() if abs(tick_df['v2p'].mean()) > 0.001 else np.nan
    factor_dict = {factor_name: cv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

