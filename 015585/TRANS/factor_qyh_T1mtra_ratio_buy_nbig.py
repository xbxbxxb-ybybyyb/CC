# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 0216提交
# 逻辑：T日09:31数据，主动买入的非大单金额占比
#
factor_name = 'qyh_T1mtra_ratio_buy_nbig'
def factor_qyh_T1mtra_ratio_buy_nbig(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.3} # 历史数据的均值

    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    # buy
    buy_amt = transaction_df[transaction_df['TradeBSFlag'] == 1].groupby('TradeBuyNo')['TradeMoney'].sum()
    buy_nbig_amt = buy_amt[buy_amt < 200000].sum()
    total_amt = transaction_df[transaction_df['TradeBSFlag'] != 0]['TradeMoney'].sum()
    # ratio
    if abs(total_amt) >= 0.001:
        ratio = buy_nbig_amt / total_amt
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
