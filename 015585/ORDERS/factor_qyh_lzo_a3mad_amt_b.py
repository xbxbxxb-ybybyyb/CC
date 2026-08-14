# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日挂单量稳定以后，挂买金额
# score:
# wu
factor_name = 'qyh_lzo_a3mad_amt_b'#
def factor_qyh_lzo_a3mad_amt_b(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 3000000}
    # 3mad
    order_df = order_df[order_df['MDTime'] >= 93000000]
    order_df['min'] = order_df['MDTime'].apply(lambda x:str(x)[:-5])
    order_df_qty = order_df.groupby('min')['OrderQty'].sum()
    med = order_df_qty.median()
    mad = abs(order_df_qty-med).median()
    limit = med + 3*mad
    time_min = order_df_qty[order_df_qty>=limit].tail(1).index()
    factor_dict = {factor_name: time_min}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
