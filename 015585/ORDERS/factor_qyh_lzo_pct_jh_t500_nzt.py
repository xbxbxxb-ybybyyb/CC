# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日,集合竞价最后500温和订单的涨跌幅
# 0.06,19
# qyh_lzo_p_b930_t500
# zcz
factor_name = 'qyh_lzo_pct_jh_t500_nzt'#
def factor_qyh_lzo_pct_jh_t500_nzt(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.0074}
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = order_df['pre_close'].max()
    if zcz == 1:
        p = pre*(1+0.098*2)
    else:
        p = pre*1.098
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[(order_df['MDTime'] <= 93000000)]

    order_df = order_df[order_df['OrderPrice'] <= p]
    order_df = order_df.tail(500) if len(order_df) >= 500 else order_df
    pct = (order_df['OrderPrice'] * order_df['OrderQty']).sum() / order_df['OrderQty'].sum() \
        if order_df['OrderQty'].sum() >0 else np.nan
    pct = pct/pre - 1 if zcz else (pct/pre - 1)/2
    factor_dict = {factor_name: pct}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
