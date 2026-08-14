# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日集合竞价，0920以前，接近涨停挂单中，大小单量价相关性的差
#
#
factor_name = 'qyh_lzo_jh1_98_corr_bs'#
def factor_qyh_lzo_jh1_98_corr_bs(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.004}
    order_df = order_df[order_df['MDTime'] < 92000000]
    pre = order_df['pre_close'].max()
    order_df = order_df[order_df['OrderPrice'] >= (pre * 1.098)]
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df1 = order_df[order_df['OrderAmt'] > 200000]
    corr1 = order_df1[['OrderQty','OrderPrice']].corr(method = 'spearman').iloc[0,1]
    order_df2 = order_df[order_df['OrderAmt'] < 50000]
    corr2 = order_df2[['OrderQty','OrderPrice']].corr(method = 'spearman').iloc[0,1]
    factor_dict = {factor_name: corr1 - corr2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
