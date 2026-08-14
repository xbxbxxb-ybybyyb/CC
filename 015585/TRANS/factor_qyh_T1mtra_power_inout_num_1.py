# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日09:31数据，买卖双方力量对比(不包括集合竞价）,聚合transaction数据，得到买卖双方单数
# score:21,10,-0.047
factor_name = 'qyh_T1mtra_power_inout_num_1'
def factor_qyh_T1mtra_power_inout_num_1(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0]
    transaction_df = transaction_df[transaction_df['TradeBSFlag'] != 0]# 集合竞价以外
    sell = len(set(transaction_df['TradeSellNo'].values))
    buy = len(set(transaction_df['TradeBuyNo'].values))
    if buy ==0:
        power = np.nan
    else:
        power = sell/buy
    factor_dict = {factor_name: power}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
