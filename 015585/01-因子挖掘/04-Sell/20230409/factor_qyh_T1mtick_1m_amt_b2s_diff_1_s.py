# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：0931，净委买金额的变化
# score:-0.07,13
# 无
factor_name = 'qyh_T1mtick_1m_amt_b2s_diff_1_s'#
def factor_qyh_T1mtick_1m_amt_b2s_diff_1_s(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # 成交额
    tick_df = tick_df[tick_df['MDTime'] >= 92500000]
    amt_df_b = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    amt_df_s = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    n = 1
    amt_1 = (amt_df_b.tail(1).mean() + amt_df_s.head(1).mean()) - (amt_df_b.head(1).mean() + amt_df_s.tail(1).mean())
    amt_2 = (amt_df_b.tail(1).mean() + amt_df_s.head(1).mean()) + (amt_df_b.head(1).mean() + amt_df_s.tail(1).mean())
    if amt_2 > 10:
        ratio = amt_1 / amt_2
    else:
        ratio = 0
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
