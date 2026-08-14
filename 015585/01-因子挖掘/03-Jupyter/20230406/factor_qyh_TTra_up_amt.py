# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：拉抬订单的总成交额
# score:0.048,10.5
# NetHBAmt:0.06,34
factor_name = 'qyh_TTra_up_amt'#
def factor_qyh_TTra_up_amt(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 38375404}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    buy_max = trans_df.groupby('TradeBuyNo')['TradePrice'].max()
    buy_min = trans_df.groupby('TradeBuyNo')['TradePrice'].min()
    buy = buy_max - buy_min
    amt = trans_df[trans_df['TradeBuyNo'].isin(list(buy[buy>0.001].index))]['TradeMoney'].sum()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
