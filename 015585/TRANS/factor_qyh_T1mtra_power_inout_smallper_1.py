# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日09:31数据，买卖双方力量对比,聚合transaction数据，得到买卖双方5万以下的小单每单金额。再相除
# score:15,6,-0.04
factor_name = 'qyh_T1mtra_power_inout_smallper_1'
def factor_qyh_T1mtra_power_inout_smallper_1(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]

    limit = 50000
    # buy
    buy_no = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']
    buy_no_small = buy_no[buy_no < limit].sum()
    buy_no_small_per = buy_no_small / len(buy_no[buy_no < limit])
    # sell
    sell_no = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    sell_no_small = sell_no[sell_no < limit].sum()
    sell_no_small_per = sell_no_small / len(sell_no[sell_no < limit])
    if abs(sell_no_small) <= 0.001:
        power = np.nan
    else:
        power = buy_no_small_per / sell_no_small_per
    factor_dict = {factor_name: power}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
