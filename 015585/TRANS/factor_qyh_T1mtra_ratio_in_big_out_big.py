# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日09:31数据 + 集合竞价，(流入部分大单 且 流出部分大单)金额占比
# score:-0.01 GG
factor_name = 'qyh_T1mtra_ratio_in_big_out_big'#del big out
def factor_qyh_T1mtra_ratio_in_big_out_big(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.4} # 历史数据的均值

    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    # buy
    buy_no = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']
    buy_no_big = buy_no[buy_no >= 200000]
    sell_no = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    sell_no_big = sell_no[sell_no >= 200000]
    buy_no_big_ob = transaction_df[(transaction_df['TradeBuyNo'].isin(buy_no_big.index)) &
                                    (transaction_df['TradeSellNo'].isin(sell_no_big.index))]['TradeMoney'].sum()
    # ratio
    if abs(buy_no.sum()) <= 0.001:
        ratio = np.nan
    else:
        ratio = buy_no_big_ob / buy_no.sum()
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
