# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：成交活跃-不活跃时，买1-买均的变异系数
# 快速：-0.1,62
# 全样本：-0.1,55
#
factor_name = 'qyh_ttick_b12b_cv_amtbs'#
def factor_qyh_ttick_b12b_cv_amtbs(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.071}
    #
    tick_df = tick_df[tick_df['MDTime'] > 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    if tick_df1.empty:
        pct1 = np.nan
    else:
        pct1 = ((tick_df1['Buy1Price'] - tick_df1['WeightedAvgBidPx']) / (tick_df1['pre_close'].max()))
        pct1 = pct1.std() / pct1.mean() if abs(pct1.mean()) > 0.00001 else np.nan
    if tick_df2.empty:
        pct2 = np.nan
    else:
        pct2 = ((tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx']) / (tick_df2['pre_close'].max()))
        pct2 = pct2.std() / pct2.mean() if abs(pct2.mean()) > 0.00001 else np.nan
    #
    factor_dict = {factor_name: pct1-pct2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
