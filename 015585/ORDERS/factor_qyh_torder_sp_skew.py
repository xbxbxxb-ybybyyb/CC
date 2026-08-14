# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 卖单价格偏度
#
#
factor_name = 'qyh_torder_sp_skew'#
def factor_qyh_torder_sp_skew(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    #
    order_df = order_df[order_df['OrderBSFlag'] == 2]
    order_df['OrderMoney'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df = order_df[order_df['OrderPrice'] > 0]
    order_df = order_df[order_df['OrderType'] == 2]
    order_df['TotalOrderQty'] = order_df['OrderQty'].cumsum()
    order_df['TotalOrderMoney'] = order_df['OrderMoney'].cumsum()
    order_df['num'] = 1
    order_df['TotalNum'] = order_df['num'].cumsum()
    order_df['p'] = order_df['OrderPrice'].cumsum()/order_df['num'].cumsum()
    w_mean = (order_df['p'] * order_df['TotalNum']).sum() / order_df['TotalNum'].sum()
    fenzi = (order_df['TotalNum'] * ((order_df['p'] - w_mean)**3)).sum() \
            / order_df['TotalNum'].sum()
    fenmu = ((order_df['TotalNum'] * ((order_df['p'] - w_mean)**2)).sum() \
            / order_df['TotalNum'].sum())**1.5
    res = fenzi / fenmu
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
