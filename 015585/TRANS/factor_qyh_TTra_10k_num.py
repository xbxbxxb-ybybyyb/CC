# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：万手大买单的数量
# score:GG,触发时一般不会有万手大单
factor_name = 'qyh_TTra_10k_num'
def factor_qyh_TTra_10k_num(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2000000}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000] # 只看成交的
    tm_buy = transaction_df.groupby('TradeBuyNo').sum()['TradeQty'] # trade_money_buy
    num = tm_buy[tm_buy > 990000].sum()

    factor_dict = {factor_name: num}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
