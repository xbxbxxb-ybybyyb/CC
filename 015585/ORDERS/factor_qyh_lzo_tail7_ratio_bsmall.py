# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日1450以后，挂买的金额为小单的比例
# score:4,0.03
# wu
factor_name = 'qyh_lzo_tail7_ratio_bsmall'#
def factor_qyh_lzo_tail7_ratio_bsmall(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.21}
    # 0930以后
    order_df = order_df[order_df['MDTime'] >= 145000000]
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df = order_df[order_df['OrderBSFlag'] == 1]
    if order_df['OrderAmt'].sum() > 0:
        ratio = order_df[order_df['OrderAmt'] < 50000]['OrderAmt'].sum() / order_df['OrderAmt'].sum()
    else:
        ratio = np.nan
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
