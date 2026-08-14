# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日,集合竞价时，非激进订单最后500单的平均涨幅
# -0.08,22
#
factor_name = 'qyh_lzo_pct_jh_n98_t500'#
def factor_qyh_lzo_pct_jh_n98_t500(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.079}
    # zcz
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    pre = order_df['pre_close'].max()
    p = pre*(1+0.098*2) if zcz else pre*1.098
    #
    order_df = order_df[order_df['OrderPrice'] <= p]
    order_df = order_df.tail(500) if len(order_df) >= 500 else order_df
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    pct = order_df['OrderAmt'].sum() / order_df['OrderQty'].sum()
    pct = pct/pre-1
    factor_dict = {factor_name: pct}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
