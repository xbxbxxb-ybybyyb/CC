# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日集合竞价，挂单金额/流动市值
# 9,-0.04
factor_name = 'qyh_lzo_amt2mv_sum'#
def factor_qyh_lzo_amt2mv_sum(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.03}
    order_df = order_df[order_df['MDTime'] < 93000000]
    mv = order_df['pre_close'].max() * order_df['ff_shares'].max()
    ratio = (order_df['OrderPrice'] * order_df['OrderQty']).sum() / mv

    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
