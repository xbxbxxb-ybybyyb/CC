# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日,早盘激进订单中，买卖单金额的变异系数
# z'c'z
#
factor_name = 'qyh_lzo_9_amt_cv_bs'#
def factor_qyh_lzo_9_amt_cv_bs(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    # zcz
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    pre = order_df['pre_close'].max()
    if zcz == 1:
        p = pre*(1+0.098*2)
    else:
        p = pre*1.098
    #
    order_df1 = order_df[(order_df['MDTime'] >= 93000000) & (order_df['MDTime'] <= 143000000)]
    order_df2 = order_df[(order_df['MDTime'] >= 143000000)]
    df1 = (order_df1['OrderQty'] * order_df1['OrderPrice'])
    df2 = (order_df2['OrderQty'] * order_df2['OrderPrice'])
    if abs(df1.mean()) > 100:
        cv1 = df1.std() / df1.mean()
    else:
        cv1 = np.nan

    if abs(df2.mean()) > 100:
        cv2 = df2.std() / df2.mean()
    else:
        cv2 = np.nan
    cv = cv1/cv2
    factor_dict = {factor_name: cv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
