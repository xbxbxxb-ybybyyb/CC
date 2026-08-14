# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日1450以后，挂卖的平均每单金额
# score:-0.02
# sss_lzo_peramt99s_close
factor_name = 'qyh_lzo_tail7_amt_s_per'#
def factor_qyh_lzo_tail7_amt_s_per(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 36179}
    # 0930以后
    order_df = order_df[order_df['MDTime'] >= 145000000]
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    amt = order_df[order_df['OrderBSFlag'] == 2]['OrderAmt'].mean()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
