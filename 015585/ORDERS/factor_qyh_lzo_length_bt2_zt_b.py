# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日,封板前挂涨停的买单数量
# 5,0
# zcz
#
factor_name = 'qyh_lzo_length_bt2_zt_b'#
def factor_qyh_lzo_length_bt2_zt_b(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1165}
    # zcz
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].max()
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    #
    order_df = order_df[order_df['MDTime'] >= 93000000]
    order_df['min'] = order_df['MDTime'].apply(lambda x:int(str(x)[:-5]))
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    #
    order_df_qty = order_df.groupby('min')['OrderQty'].sum()
    time_min = order_df_qty[order_df_qty>=order_df_qty.quantile(0.95)].tail(1).index.values[0]
    time_min = time_min * 100000
    order_df = order_df[order_df['MDTime'] <= time_min]
    #
    order_df = order_df[order_df['OrderPrice'] >= p_zt]
    length = len(order_df[order_df['OrderBSFlag']==1])
    factor_dict = {factor_name: length}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
