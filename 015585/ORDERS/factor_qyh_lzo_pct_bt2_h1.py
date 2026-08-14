# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日,开盘后的挂单均价
# 0.065,32
# zcz
#
factor_name = 'qyh_lzo_pct_bt2_h1'#
def factor_qyh_lzo_pct_bt2_h1(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.041}
    pre_close = order_df['pre_close'].max()
    order_df = order_df[order_df['MDTime'] >= 93000000]
    order_df['min'] = order_df['MDTime'].apply(lambda x:int(str(x)[:-5]))
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    #
    order_df_qty = order_df.groupby('min')['OrderQty'].sum()
    time_min = order_df_qty[order_df_qty>=order_df_qty.quantile(0.95)].tail(1).index.values[0]
    time_min = time_min * 100000
    order_df = order_df[order_df['MDTime'] <= time_min]
    order_df = order_df.head(int(len(order_df)/2))
    #
    if order_df['OrderQty'].sum() > 10:
        p = (order_df['OrderPrice'] * order_df['OrderQty']).sum() / order_df['OrderQty'].sum()
    else:
        p = np.nan

    if pre_close > 0.1:
        pct = p / pre_close - 1
        # zcz
        dt, ticker = order_df.index[0]
        dt = dt.strftime('%Y%m%d')
        zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
        if zcz:
            pct = pct / 2
    else:
        pct = np.nan
    factor_dict = {factor_name: pct}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
