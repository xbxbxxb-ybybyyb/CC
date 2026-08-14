# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：买1-买均在后一半tick中上涨的均值
# 快速:
# 全样本：
#
factor_name = 'qyh_ttick_b12b_h2_mean_h'#
def factor_qyh_ttick_b12b_h2_mean_h(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.01}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    #
    tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df1 = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    tick_df1 = tick_df1.tail(int(len(tick_df1)/2))
    # tick_df2 = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    # tick_df2 = tick_df2.tail(int(len(tick_df2)/2))
    #
    factor1 = ((tick_df1['Buy1Price'] - tick_df1['WeightedAvgBidPx']) / (tick_df1['pre_close'].max())).mean()
    # factor2 = ((tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx']) / (tick_df2['pre_close'].max())).mean()
    factor_dict = {factor_name: factor1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
