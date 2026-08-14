# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日1450以后，挂买的金额为涨停价的比例
# score:0.06,7
# wu
factor_name = 'qyh_lzo_tail7_ratio_bzt'#
def factor_qyh_lzo_tail7_ratio_bzt(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.8}
    # 0930以后
    order_df = order_df[order_df['MDTime'] >= 145000000]
    pre_close = round(order_df['pre_close'].mean(),3)
    if order_df.empty:
        ratio = np.nan
    else:
        ticker = order_df['HTSCSecurityID'][0]
        dt = order_df['MDDate'][0]
        zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
        if zcz:
            p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
        else:
            p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100

        if len(order_df)>0:
            ratio = len(order_df[order_df['OrderPrice'] >= p_zt]) / len(order_df)
        else:
            ratio = np.nan
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
