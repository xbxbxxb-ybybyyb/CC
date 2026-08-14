# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日09:31数据，主动买单的每单成交额（不包括集合竞价）的标准差（除以均值） - 主动卖单的xxx，衡量主动交易者的复杂度差异
# score:GG
#
factor_name = 'qyh_T1mtra_amtpertra_buysell_s'
def factor_qyh_T1mtra_amtpertra_buysell_s(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 16751}
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0)]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0]#只看成交
    # buy
    transaction_df_buy = transaction_df[transaction_df['TradeBSFlag'] == 1]#主动买单
    transaction_df_buy = transaction_df_buy.groupby('TradeBuyNo').sum()['TradeMoney']#聚合
    if transaction_df_buy.empty:
        amtpertra_in = 0
    else:
        amtpertra_in = transaction_df_buy.std() / transaction_df_buy.mean()
    # sell
    transaction_df_sell = transaction_df[transaction_df['TradeBSFlag'] == 2]  # 主动卖单
    transaction_df_sell = transaction_df_sell.groupby('TradeSellNo').sum()['TradeMoney']  # 聚合
    if transaction_df_sell.empty:
        amtpertra_out = 0
    else:
        amtpertra_out = transaction_df_sell.std() / transaction_df_sell.mean()
    power = amtpertra_in/amtpertra_out if abs(amtpertra_out) >0.01 else np.nan
    factor_dict = {factor_name: power}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
