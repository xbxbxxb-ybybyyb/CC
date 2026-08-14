# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：买单集中度：主动买单的平方和 / 总平方和（>0)
# score:6，3，-0.025
#
factor_name = 'qyh_T1mtra_cct_buy'#concenteration
def factor_qyh_T1mtra_cct_buy(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    tm_buy_df = transaction_df[transaction_df['TradeBSFlag'] == 1] # 主动买
    tm_buy = tm_buy_df.groupby('TradeBuyNo').sum()['TradeMoney'] # trade_money_buy
    total_buy = transaction_df['TradeMoney'].sum()
    if abs(total_buy) <= 1:
        buy_cct = np.nan
    else:
        buy_cct = (tm_buy ** 2).sum() / tm_buy_df['TradeMoney'].sum() ** 2
    factor_dict = {factor_name: buy_cct}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
