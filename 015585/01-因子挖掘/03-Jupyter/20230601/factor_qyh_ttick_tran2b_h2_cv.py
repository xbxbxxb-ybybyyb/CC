# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：成交价-买均在后1/2时间上的变异系数
# 快速:62,-0.11（1/2），取1/4差不多，但corr变高
# 全样本：66,-0.12（1/2）
#
factor_name = 'qyh_ttick_tran2b_h2_cv'#
def factor_qyh_ttick_tran2b_h2_cv(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.2}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df.tail(int(len(tick_df) / 2))

    #
    tick_df['factor'] = (tick_df['ValueTrade'] / tick_df['VolumeTrade'] - tick_df['WeightedAvgBidPx']) / (tick_df['pre_close'].max())
    cv = tick_df['factor'].std() / tick_df['factor'].mean() if abs(tick_df['factor'].mean()) > 0.0001 else np.nan
    factor_dict = {factor_name: cv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
