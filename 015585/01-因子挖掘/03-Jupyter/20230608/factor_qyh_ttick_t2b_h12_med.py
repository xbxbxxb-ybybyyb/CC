# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：前一半/后一半，tick中成交价格-挂买均价对应的涨跌幅的中位数
# 快速:0
# 全样本：
#
factor_name = 'qyh_ttick_t2b_h12_med'#
def factor_qyh_ttick_t2b_h12_med(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.01}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df1 = tick_df.head(int(len(tick_df)/2))
    t2b1 = ((tick_df1['ValueTrade'] / tick_df1['VolumeTrade'] - tick_df1['WeightedAvgBidPx']) / (tick_df1['pre_close'].max())).median()

    tick_df2 = tick_df.tail(int(len(tick_df)/2))
    t2b2 = ((tick_df2['ValueTrade'] / tick_df2['VolumeTrade'] - tick_df2['WeightedAvgBidPx']) / (tick_df2['pre_close'].max())).median()
    factor_dict = {factor_name: t2b1 / t2b2 if t2b2 != 0 else np.nan}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
