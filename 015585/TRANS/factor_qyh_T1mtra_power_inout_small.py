# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待考察构成因子的情况
# 逻辑：T日09:31数据，买卖双方力量对比(包括集合竞价）,聚合transaction数据，factor = 买卖双方20万以下的小单总额力量对比 - 小单每单金额力量对比
# score:17,8,0.03:在小单方面，买单力量越强，越容易高开低走


factor_name = 'qyh_T1mtra_power_inout_small'
def factor_qyh_T1mtra_power_inout_small(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.84}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    limit = 50000
    # buy
    buy_no = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']
    buy_no_small = buy_no[buy_no < limit]
    buy_no_small_total = buy_no_small.sum()
    len_buy_no_small = len(buy_no_small)
    if len_buy_no_small == 0:
        buy_no_small_per = np.nan
    else:
        buy_no_small_per = buy_no_small_total / len_buy_no_small
    # sell
    sell_no = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    sell_no_small = sell_no[sell_no < limit]
    sell_no_small_total = sell_no_small.sum()
    len_sell_no_small = len(sell_no_small)
    if len_sell_no_small == 0:
        sell_no_small_per = np.nan
    else:
        sell_no_small_per = sell_no_small_total / len_sell_no_small
    # power1,power2
    if abs(sell_no_small_total) <= 0.001:
        power_total = np.nan
    else:
        power_total = buy_no_small_total / sell_no_small_total
    if abs(sell_no_small_per) <= 0.001:
        power_per = np.nan
    else:
        power_per = buy_no_small_per / sell_no_small_per
    factor_dict = {factor_name: power_total - power_per}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
