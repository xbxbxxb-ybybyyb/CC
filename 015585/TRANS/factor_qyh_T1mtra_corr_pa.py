# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：量价相关性（包括集合竞价)
# 5，0.027
factor_name = 'qyh_T1mtra_corr_pa'#price and amt
def factor_qyh_T1mtra_corr_pa(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    pa = transaction_df.groupby('TradePrice').sum()['TradeMoney']# 不同价位下的成交金额
    pa_corr = pa.reset_index().corr().loc['TradePrice','TradeMoney']
    factor_dict = {factor_name: pa_corr}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
