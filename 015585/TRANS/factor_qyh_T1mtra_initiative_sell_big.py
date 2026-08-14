# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日主动成交度-大单卖出：大卖单主动成交金额 / 大卖单成交金额
# 8，4，-0.02
# wd_t1_act_vol_pct
factor_name = 'qyh_T1mtra_initiative_sell_big'
def factor_qyh_T1mtra_initiative_sell_big(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.37} # 历史数据的均值

    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    transaction_df = transaction_df[transaction_df['TradeBSFlag'] != 0] # 0931
    # sell_big
    sell_big = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    sell_big = sell_big[sell_big > 200000]
    sell_big_ini = transaction_df[transaction_df['TradeSellNo'].isin(sell_big.index)]
    sell_big_ini = sell_big_ini[sell_big_ini['TradeBSFlag'] == 2]['TradeMoney'].sum()
    if sell_big.sum() > 100:
        ratio = sell_big_ini / sell_big.sum()
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
