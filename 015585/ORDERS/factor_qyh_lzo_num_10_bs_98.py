# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日,早盘激进订单中大小单个数比
# 0.07,25 repeat高，改进一下0.069,20
#
# zcz
factor_name = 'qyh_lzo_num_10_bs_98'#
def factor_qyh_lzo_num_10_bs_98(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.057}
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = order_df['pre_close'].max()
    if zcz == 1:
        p = pre*(1+0.098*2)
    else:
        p = pre*1.098
    #
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[(order_df['MDTime'] >= 93000000) & (order_df['MDTime'] <= 100000000)]
    order_df = order_df[order_df['OrderPrice'] >= p]
    num1 = len(order_df[order_df['OrderAmt'] >= 200000])
    num2 = len(order_df[order_df['OrderAmt'] <= 50000])
    if num1 > 0:
        ratio = num1/num2 if num2 > 0 else np.nan
    else:
        ratio = len(order_df[order_df['OrderAmt'] >= 50000])/num2 if num2>0 else np.nan
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
