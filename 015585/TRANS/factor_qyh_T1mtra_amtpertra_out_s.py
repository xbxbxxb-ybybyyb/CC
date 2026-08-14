# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日09:31数据(包括集合竞价）,卖单平均每单（非每笔）金额的标准差（除以均值），衡量投资者的复杂程度 # 尝试不除以均值 gg
# score:GG
factor_name = 'qyh_T1mtra_amtpertra_out_s'
def factor_qyh_T1mtra_amtpertra_out_s(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    # sell
    sell_no = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    std_per_tran_out = sell_no.std() / sell_no.mean()
    factor_dict = {factor_name: std_per_tran_out}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
