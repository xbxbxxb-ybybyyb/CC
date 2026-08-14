# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日,非早盘挂单的集中度
# 0,3
#
factor_name = 'qyh_lzo_amt_cct_a10'#
def factor_qyh_lzo_amt_cct_a10(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.02}
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[(order_df['MDTime'] >= 100000000)]
    cct = order_df['OrderAmt'].std() / order_df['OrderAmt'].mean() if order_df['OrderAmt'].mean()>0 else np.nan
    factor_dict = {factor_name: cct}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
