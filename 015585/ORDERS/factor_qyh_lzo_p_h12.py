# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日前一半和后一半订单挂单均价的比值
# 11,0.038
# wu
factor_name = 'qyh_lzo_p_h12'#
def factor_qyh_lzo_p_h12(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.96}
    # 0930以后
    order_df = order_df[(order_df['MDTime'] >= 93000000)]
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df1 = order_df.head(int(len(order_df)/2))
    order_df2 = order_df.tail(int(len(order_df)/2))
    p1 = order_df1['OrderAmt'].sum() / order_df1['OrderQty'].sum()
    p2 = order_df2['OrderAmt'].sum() / order_df2['OrderQty'].sum()
    if p2 > 0.5:
        ratio = p1 / p2
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
