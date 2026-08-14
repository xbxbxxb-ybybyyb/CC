# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日涨停挂单稳定以后，新增挂买/新增挂卖
# score:0，0
# 无
factor_name = 'qyh_lzo_a95_ratio_b2s'#
def factor_qyh_lzo_a95_ratio_b2s(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2}
    # 0930以后
    order_df = order_df[order_df['MDTime'] >= 93000000]
    order_df['min'] = order_df['MDTime'].apply(lambda x: int(str(x)[:-5]))
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    #
    order_df_qty = order_df.groupby('min')['OrderQty'].sum()
    time_min = order_df_qty[order_df_qty >= order_df_qty.quantile(0.95)].tail(1).index.values[0]
    #
    order_df_azt = order_df[(order_df['min'] > time_min) & (order_df['OrderBSFlag'] == 1)]#涨停以后的部分
    order_df_amt = order_df_azt['OrderQty'] * order_df_azt['OrderPrice']
    amt_1 = order_df_amt.sum()
    order_df_azt = order_df[(order_df['min'] > time_min) & (order_df['OrderBSFlag'] == 2)]#涨停以后的部分
    order_df_amt = order_df_azt['OrderQty'] * order_df_azt['OrderPrice']
    amt_2 = order_df_amt.sum()
    if amt_2 > 10:
        ratio = amt_1 / amt_2
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
