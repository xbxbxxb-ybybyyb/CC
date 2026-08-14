# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日主动成交度-小单买入：小买单主动成交金额 / 小买单成交金额
# 14，7，0.05
factor_name = 'qyh_T1mtra_initiative_buy_small'
def factor_qyh_T1mtra_initiative_buy_small(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5} # 历史数据的均值

    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    transaction_df = transaction_df[transaction_df['TradeBSFlag'] != 0] # 0931
    # buy_small
    buy_small = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']
    buy_small = buy_small[buy_small < 50000]
    buy_small_ini = transaction_df[transaction_df['TradeBuyNo'].isin(buy_small.index)]
    buy_small_ini = buy_small_ini[buy_small_ini['TradeBSFlag'] == 1]['TradeMoney'].sum()
    if buy_small.sum() > 100:
        ratio = buy_small_ini / buy_small.sum()
    else :
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
