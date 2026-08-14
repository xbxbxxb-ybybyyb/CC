# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：ret > 0.09，成交额占比
# score: 43,0.08
# Institute_earn:0.13
factor_name = 'qyh_T1mtra_amt_ratio_p9'#concenteration,qyh_T1mtra_buy_cct
def factor_qyh_T1mtra_amt_ratio_p9(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.07}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000] # 只看成交的
    pre_close = transaction_df['pre_close'].mean()
    amt_p9 = transaction_df[transaction_df['TradePrice'] >= pre_close*1.09]['TradeMoney'].sum()
    amt_total = transaction_df['TradeMoney'].sum()
    ratio = amt_p9 / amt_total
    factor_dict = {factor_name: ratio}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
