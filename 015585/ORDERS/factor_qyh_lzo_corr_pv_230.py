# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日尾盘前的量价相关性
# -0.03,3
#
factor_name = 'qyh_lzo_corr_pv_230'#
def factor_qyh_lzo_corr_pv_230(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.004}
    order_df = order_df[order_df['MDTime'] <= 143000000]
    order_df = order_df.tail(500)
    corr = order_df[['OrderQty','OrderPrice']].corr(method = 'spearman').iloc[0,1]
    factor_dict = {factor_name: corr}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
