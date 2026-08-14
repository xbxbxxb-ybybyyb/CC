# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：活跃与不活跃tick中，买1-买均在触发前的差值
# 快速:59，-0.1
# 全样本：61，-0.11
#
factor_name = 'qyh_ttick_b12b_tail_amt'#
def factor_qyh_ttick_b12b_tail_amt(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.01}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    #
    pct1 = ((tick_df1['Buy1Price'] - tick_df1['WeightedAvgBidPx']) / (tick_df1['pre_close'].max())).tail(1).mean()
    pct2 = ((tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx']) / (tick_df2['pre_close'].max())).tail(1).mean()
    factor_dict = {factor_name: pct1 - pct2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
