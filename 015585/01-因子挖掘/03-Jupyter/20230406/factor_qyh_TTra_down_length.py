# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：打压订单的总数量
# score:0.048,7
# xbc_exchange_ratio_diff
factor_name = 'qyh_TTra_down_length'#
def factor_qyh_TTra_down_length(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 203}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    buy_max = trans_df.groupby('TradeSellNo')['TradePrice'].max()
    buy_min = trans_df.groupby('TradeSellNo')['TradePrice'].min()
    buy = buy_max - buy_min
    length = len(buy[buy>0])
    # if length > 1000:
    #     length = 1000
    factor_dict = {factor_name: length}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
