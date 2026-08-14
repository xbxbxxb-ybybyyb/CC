# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日集合竞价,前一半订单，买卖单挂单价比例
# 0.02，2
# wd_lzo_open_p_bda
factor_name = 'qyh_lzo_p_jt_1_buysell'#
def factor_qyh_lzo_p_jt_1_buysell(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.92}
    # 0930以后
    order_df = order_df[(order_df['MDTime'] < 93000000)]
    order_df = order_df.head(int(len(order_df)/2))
    # order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df_buy = order_df[order_df['OrderBSFlag'] == 1]
    order_df_sell = order_df[order_df['OrderBSFlag'] == 2]
    p_buy = (order_df_buy['OrderQty'] * order_df_buy['OrderPrice']).sum() / (order_df_buy['OrderQty'].sum())
    p_sell = (order_df_sell['OrderQty'] * order_df_sell['OrderPrice']).sum() / (order_df_sell['OrderQty'].sum())
    if p_sell > 0.5:
        ratio = p_buy / p_sell
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
