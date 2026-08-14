# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：买单每单委托金额
# 快速：13，0
# 全样本：1，0
#
factor_name = 'qyh_torder_peramt_s'#
def factor_qyh_torder_peramt_s(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 28428}
    order_df = order_df[order_df['MDTime'] > 93000000]
    order_df = order_df[order_df['OrderBSFlag'] == 2]
    if order_df.empty:
        amt = np.nan
    else:
        amt = (order_df['OrderPrice'] * order_df['OrderQty']).mean()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
