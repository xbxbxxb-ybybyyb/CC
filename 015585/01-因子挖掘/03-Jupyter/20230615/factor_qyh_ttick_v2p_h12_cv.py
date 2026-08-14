# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：vwap和最新价的比值在前一半-后一半的变异系数
# 快速:等权，50，-0.07
# 全样本：
#
factor_name = 'qyh_ttick_v2p_h12_cv'#
def factor_qyh_ttick_v2p_h12_cv(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df1 = tick_df.head(int(len(tick_df)/2))
    tick_df2 = tick_df.tail(int(len(tick_df)/2))
    #
    tick_df1['vwap'] = tick_df1['ValueTrade'].cumsum()/tick_df1['VolumeTrade'].cumsum()
    mean1 = (tick_df1['vwap']/tick_df1['LastPx']).mean()
    std1 = (tick_df1['vwap']/tick_df1['LastPx']).std()
    cv1 = std1 / mean1 if mean1 != 0 else std1
    #
    tick_df2['vwap'] = tick_df2['ValueTrade'].cumsum()/tick_df2['VolumeTrade'].cumsum()
    mean2 = (tick_df2['vwap']/tick_df2['LastPx']).mean()
    std2 = (tick_df2['vwap']/tick_df2['LastPx']).std()
    cv2 = std2 / mean2 if mean2 != 0 else std2
    factor_dict = {factor_name: cv1/0.18-cv2/0.028}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
