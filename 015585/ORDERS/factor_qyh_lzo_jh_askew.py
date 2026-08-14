# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日集合竞价的偏度
# -0.009,2,0.066
# wu
factor_name = 'qyh_lzo_jh_askew'#
def factor_qyh_lzo_jh_askew(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 6.7}
    order_df = order_df[order_df['MDTime'] < 92000000]
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    skew = order_df['OrderAmt'].skew()
    factor_dict = {factor_name: skew}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
