# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日1450以后，卖单平均每单大小的分位数
# score:3,-0.02
# wu
factor_name = 'qyh_lzo_tail7_s_per_pct'#
def factor_qyh_lzo_tail7_s_per_pct(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.74}
    #
    qty = order_df[(order_df['MDTime'] >= 93000000) & (order_df['OrderBSFlag'] == 2)]['OrderQty']
    #
    order_df = order_df[order_df['MDTime'] >= 145000000]
    tail_amt = order_df[order_df['OrderBSFlag'] == 2]['OrderQty'].mean() # 尾盘每单大小
    #
    list_qty = list(qty)
    list_qty.append(tail_amt)
    if len(qty) >0:
        ratio = pd.Series(list_qty).rank().tail(1).max() / len(qty)
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
