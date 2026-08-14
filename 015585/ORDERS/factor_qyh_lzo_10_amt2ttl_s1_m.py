# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日,早盘挂卖中，每单金额/当日总挂单的均值商
# 0.115,54
# yzhan_hf_ac9_26,wd_lzkcs_notul_amt_d_max
factor_name = 'qyh_lzo_10_amt2ttl_s1_m'#
def factor_qyh_lzo_10_amt2ttl_s1_m(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    #
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    ttl = order_df['OrderAmt'].sum()
    order_df = order_df[(order_df['MDTime'] >= 93000000) & (order_df['MDTime'] <= 100000000)]
    order_df['OrderAmt2ttl'] = order_df['OrderAmt'] / ttl
    ratio1 = order_df[order_df['OrderBSFlag'] == 2]['OrderAmt2ttl'].mean()

    factor_dict = {factor_name: ratio1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
