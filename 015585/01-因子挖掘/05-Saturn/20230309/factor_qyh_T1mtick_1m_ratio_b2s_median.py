# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：0931，挂买/挂卖的Median
# score:55,31,0.08
# wd_k1_bid_d_ask_median:49,28,0.079
factor_name = 'qyh_T1mtick_1m_ratio_b2s_median'#
def factor_qyh_T1mtick_1m_ratio_b2s_median(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    ratio = (tick_df['WeightedAvgBidPx'] * tick_df['TotalBidQty']/
             (tick_df['WeightedAvgOfferPx'] * tick_df['TotalOfferQty'])).median()
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
