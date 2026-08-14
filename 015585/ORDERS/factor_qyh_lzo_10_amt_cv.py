# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日,早盘订单金额的变异系数/长度
# 70,0.152(cv/length)
# 一大堆
factor_name = 'qyh_lzo_10_amt_cv'#
def factor_qyh_lzo_10_amt_cv(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.00017}
    #
    order_df = order_df[order_df['MDTime'] >= 93000000]
    length = len(order_df)
    #
    order_df = order_df[(order_df['MDTime'] <= 100000000)]
    order_df['OrderAmt'] = (order_df['OrderQty'] * order_df['OrderPrice'])
    if order_df.empty:
        cv = np.nan
    else:
        cv = order_df['OrderAmt'].std() / order_df['OrderAmt'].mean()
        cv = cv / length

    factor_dict = {factor_name: cv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
