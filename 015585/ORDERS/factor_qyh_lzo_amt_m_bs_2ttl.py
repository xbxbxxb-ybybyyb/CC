# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日早盘大小单每单量占当日总挂单量的比例商
# 若小单占总挂单量比例过低，认为结果失真，取ratio2
# 0.115,22
factor_name = 'qyh_lzo_amt_m_bs_2ttl'#
def factor_qyh_lzo_amt_m_bs_2ttl(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 28}
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[(order_df['MDTime'] >= 93000000)]
    ttl = order_df['OrderAmt'].sum()
    order_df = order_df[(order_df['MDTime'] <= 100000000)]
    order_df1 = order_df[order_df['OrderAmt'] > 200000]
    order_df2 = order_df[order_df['OrderAmt'] < 50000]
    ratio1 = order_df1['OrderAmt'].mean() / ttl
    ratio2 = order_df2['OrderAmt'].mean() / ttl
    lim = 0.00001
    if ratio2 > lim:
        ratio = ratio1/ratio2
    else:
        ratio = ratio2/lim*10
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
