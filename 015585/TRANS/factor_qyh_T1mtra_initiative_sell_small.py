# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日主动成交度-小单卖出：小卖单主动成交金额 / 小卖单成交金额
# 13，7，-0.05
factor_name = 'qyh_T1mtra_initiative_sell_small'
def factor_qyh_T1mtra_initiative_sell_small(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5} # 历史数据的均值

    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    transaction_df = transaction_df[transaction_df['TradeBSFlag'] != 0] # 0931
    # sell_small
    sell_small = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    sell_small = sell_small[sell_small < 50000]
    sell_small_ini = transaction_df[transaction_df['TradeSellNo'].isin(sell_small.index)]
    sell_small_ini = sell_small_ini[sell_small_ini['TradeBSFlag'] == 2]['TradeMoney'].sum()
    if sell_small.sum() > 100:
        ratio = sell_small_ini / sell_small.sum()
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
