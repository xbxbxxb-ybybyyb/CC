# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日激进订单中大小单总金额之比
# zcz
# 15，0.077
factor_name = 'qyh_lzo_bs_9_amt'#
def factor_qyh_lzo_bs_9_amt(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 6.37}
    # zcz
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    order_df = order_df[(order_df['MDTime'] >= 93000000) & (order_df['MDTime'] <= 143000000)]
    pre = order_df['pre_close'].max()
    if zcz == 1:
        p = pre*(1+0.098*2)
    else:
        p = pre*1.098
    #
    order_df = order_df[order_df['OrderPrice'] >= p]
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    df1 = order_df[order_df['OrderAmt'] >= 200000]
    df2 = order_df[order_df['OrderAmt'] <= 50000]
    amt1 = (df1['OrderAmt']).sum()
    amt2 = (df2['OrderAmt']).sum()
    if amt2 > 100:
        num = amt1 / amt2
    else:
        num = np.nan
    factor_dict = {factor_name: num}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
