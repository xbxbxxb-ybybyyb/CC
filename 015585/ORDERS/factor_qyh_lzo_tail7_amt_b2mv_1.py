# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日1450以后，ln挂买的金额/ln流动市值
# score:-0.12,21.8
# wd_lzo_close7_bid_amt
factor_name = 'qyh_lzo_tail7_amt_b2mv_1'#
def factor_qyh_lzo_tail7_amt_b2mv_1(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 11}
    # 0930以后
    order_df = order_df[order_df['MDTime'] >= 145000000]
    amt = (order_df[order_df['OrderBSFlag'] == 1]['OrderQty'] * order_df[order_df['OrderBSFlag'] == 1]['OrderPrice']).sum()
    mv = order_df['pre_close'].max()*order_df['ff_shares'].max()
    if mv > 0:
        ratio = np.log(amt)/np.log(mv)
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
