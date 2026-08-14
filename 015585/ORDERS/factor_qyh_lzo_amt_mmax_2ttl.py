# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日早盘最大Order占当日总挂单量的比例
# 0.113,23
# wu
factor_name = 'qyh_lzo_amt_mmax_2ttl'#
def factor_qyh_lzo_amt_mmax_2ttl(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.003}
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[(order_df['MDTime'] >= 93000000)]
    ttl = order_df['OrderAmt'].sum()
    order_df = order_df[(order_df['MDTime'] <= 100000000)]
    if ttl >0:
        ratio = order_df['OrderAmt'].max()/ttl
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
