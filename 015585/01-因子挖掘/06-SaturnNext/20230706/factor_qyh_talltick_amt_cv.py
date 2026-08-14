# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# tick成交量的变异系数
# 22,-0.04
def factor_qyh_talltick_amt_cv(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_amt_cv'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 3.06}
    pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    amt_cv = tick_df['ValueTrade'].std() / tick_df['ValueTrade'].mean() if tick_df['ValueTrade'].mean()>0 else np.nan
    factor_dict = {factor_name: amt_cv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

