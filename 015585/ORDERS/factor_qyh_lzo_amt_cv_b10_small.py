# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日,早盘大单的变异系数
# 0,0
#
factor_name = 'qyh_lzo_amt_cv_b10_small'#
def factor_qyh_lzo_amt_cv_b10_small(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = order_df['pre_close'].max()
    if zcz == 1:
        p = pre*(1+0.095*2)
    else:
        p = pre*1.095
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[(order_df['MDTime'] >= 93000000) & (order_df['MDTime'] <= 100000000)]
    # order_df1 = order_df[order_df['OrderPrice'] >= 200000]
    order_df2 = order_df[order_df['OrderAmt'] < 50000]
    # f1 = order_df1['OrderAmt'].std() / order_df1['OrderAmt'].mean() if order_df1['OrderAmt'].mean()!=0 else 0
    f2 = order_df2['OrderAmt'].std() / order_df2['OrderAmt'].mean() if order_df2['OrderAmt'].mean()!=0 else 0
    # factor = f1/f2 if f2 != 0 else np.nan
    factor_dict = {factor_name: f2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
