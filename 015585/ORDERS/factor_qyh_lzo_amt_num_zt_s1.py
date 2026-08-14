# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日,早盘涨停订单的卖单数目
# 0.02,6
#
factor_name = 'qyh_lzo_amt_num_zt_s1'#
def factor_qyh_lzo_amt_num_zt_s1(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 6000}
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = order_df['pre_close'].max()
    if zcz == 1:
        p = pre*(1+0.1*2)
    else:
        p = pre*1.1
    # order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[(order_df['MDTime'] >= 93000000) & (order_df['MDTime'] <= 100000000)]

    if len(order_df[order_df['OrderPrice'] >= p]) == 0:
        order_df = order_df[order_df['OrderPrice'] >= order_df['OrderPrice'].quantile(0.9)]
    else:
        order_df = order_df[order_df['OrderPrice'] >= p]
    len1 = len(order_df[order_df['OrderBSFlag'] == 2])
    if len1 == 0:
        len1 = len(order_df[order_df['OrderPrice'] == order_df['OrderPrice'].max()])
    factor_dict = {factor_name: len1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
