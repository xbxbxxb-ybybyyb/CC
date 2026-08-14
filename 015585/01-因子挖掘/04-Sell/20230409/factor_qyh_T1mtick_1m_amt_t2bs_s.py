# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：0931，std(委买/成交) - std(委卖/成交)
# 13,6,-0.04
factor_name = 'qyh_T1mtick_1m_amt_t2bs_s'#
def factor_qyh_T1mtick_1m_amt_t2bs_s(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.1}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    std_b = (tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'] / tick_df['amt']).std()
    std_s = (tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx'] / tick_df['amt']).std()
    factor_dict = {factor_name: std_b - std_s}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
