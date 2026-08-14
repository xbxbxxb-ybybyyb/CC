# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日开盘后，高价与低价订单的量价相关性的差
# -0.03,3,0.053
# wu
# zcz
factor_name = 'qyh_lzo_98_corr'#
def factor_qyh_lzo_98_corr(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.03}
    order_df = order_df[order_df['MDTime'] > 93000000]
    pre = order_df['pre_close'].max()
    ticker = order_df['HTSCSecurityID'][0]
    dt = order_df['MDDate'][0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    if zcz:
        a = 1 + (0.098)*2
    else:
        a = 1.098
    order_df1 = order_df[order_df['OrderPrice'] >= (pre * a)]
    corr1 = order_df1[['OrderQty','OrderPrice']].corr(method = 'spearman').iloc[0,1]
    order_df2 = order_df[order_df['OrderPrice'] < (pre * a)]
    corr2 = order_df2[['OrderQty','OrderPrice']].corr(method = 'spearman').iloc[0,1]
    factor_dict = {factor_name: corr1 - corr2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
