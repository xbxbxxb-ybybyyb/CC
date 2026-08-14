# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：T日大买单主动成交度 - T日大卖单主动成交度
# 11，4，0.038

factor_name = 'qyh_T1mtra_initiative_bs_big'
def factor_qyh_T1mtra_initiative_bs_big(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5} # 历史数据的均值

    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    transaction_df = transaction_df[transaction_df['TradeBSFlag'] != 0] # 0931
    # buy_big
    buy_big = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']
    buy_big = buy_big[buy_big > 200000]
    buy_big_ini = transaction_df[transaction_df['TradeBuyNo'].isin(buy_big.index)]
    buy_big_ini = buy_big_ini[buy_big_ini['TradeBSFlag'] == 1]['TradeMoney'].sum()
    if buy_big.sum() > 100:
        ratio_1 = buy_big_ini / buy_big.sum()
    else :
        ratio_1 = np.nan
    # sell_big
    sell_big = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    sell_big = sell_big[sell_big > 200000]
    sell_big_ini = transaction_df[transaction_df['TradeSellNo'].isin(sell_big.index)]
    sell_big_ini = sell_big_ini[sell_big_ini['TradeBSFlag'] == 2]['TradeMoney'].sum()
    if sell_big.sum() > 100:
        ratio_2 = sell_big_ini / sell_big.sum()
    else :
        ratio_2 = np.nan
    factor_dict = {factor_name: ratio_1 - ratio_2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
