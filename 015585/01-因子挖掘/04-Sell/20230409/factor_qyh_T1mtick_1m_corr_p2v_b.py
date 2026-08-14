# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：0931，每个tick挂买均价和挂买量的corr
# score:0.01,0.8,GG
# GG
factor_name = 'qyh_T1mtick_1m_corr_p2v_b'#
def factor_qyh_T1mtick_1m_corr_p2v_b(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    # 成交额
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    corr = tick_df[['TotalBidQty','WeightedAvgBidPx']].corr(method = 'spearman').iloc[0,1]
    # tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'] + tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']#
    factor_dict = {factor_name: corr}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
