# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：0931，净委买金额的变化
# score:8,-0.06
# sss_tk1m_amtdiff_chg:-0.08
factor_name = 'qyh_T1mtick_1m_amt_b2s_diff_3'#
def factor_qyh_T1mtick_1m_amt_b2s_diff_3(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # 成交额
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    amt_df = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'] - tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    n = 3
    amt_delta = amt_df.tail(3).mean() - amt_df.head(3).mean()
    factor_dict = {factor_name: amt_delta}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
