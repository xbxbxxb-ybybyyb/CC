# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日尾盘前，激进大单的买卖个数比
# zcz
# 17，0.09
factor_name = 'qyh_lzo_b_9bs_l'#
def factor_qyh_lzo_b_9bs_l(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2.14}
    # zcz
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    order_df = order_df[(order_df['MDTime'] >= 93000000) & (order_df['MDTime'] <= 143000000)]
    pre = order_df['pre_close'].max()
    if zcz == 1:
        p = pre*(1+0.09*2)
    else:
        p = pre*1.09
    #
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[(order_df['OrderPrice'] >= p) & (order_df['OrderAmt'] >= 200000)]
    num1 = len(order_df[order_df['OrderBSFlag'] == 1])
    num2 = len(order_df[order_df['OrderBSFlag'] == 2])
    if num2 > 1:
        num = num1 / num2
    else:
        num = num1
    factor_dict = {factor_name: num}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
