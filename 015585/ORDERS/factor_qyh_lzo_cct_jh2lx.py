# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日集合竞价/非集合竞价的挂单金额集中度
# -0.115
# wu
factor_name = 'qyh_lzo_cct_jh2lx'#
def factor_qyh_lzo_cct_jh2lx(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    order_df1 = order_df[order_df['MDTime'] < 93000000]
    order_df1['OrderAmt'] = order_df1['OrderQty'] * order_df1['OrderPrice']
    cct1 = (order_df1['OrderAmt']**2).sum() / (order_df1['OrderAmt'].sum()**2)

    order_df2 = order_df[order_df['MDTime'] > 93000000]
    order_df2['OrderAmt'] = order_df2['OrderQty'] * order_df2['OrderPrice']
    cct2 = (order_df2['OrderAmt']**2).sum() / (order_df2['OrderAmt'].sum()**2)
    factor_dict = {factor_name: cct1/cct2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
