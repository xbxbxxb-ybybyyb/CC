# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
factor_name = 'qyh_T1mtra_r_amt2pct_down_big_1'#
def factor_qyh_T1mtra_r_amt2pct_down_big_1(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -5}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] #
    transaction_df['last_price'] = transaction_df['TradePrice'].shift(1) #
    mv = transaction_df['pre_close'][0] * transaction_df['ff_shares'][0]
    transaction_df_down = transaction_df[transaction_df['TradeBSFlag'] == 2]#
    transaction_df_down_big = transaction_df_down.groupby('TradeSellNo')['TradeMoney'].sum()
    transaction_df_down_big = transaction_df_down_big[transaction_df_down_big > 200000]#
    transaction_df_down = transaction_df_down[transaction_df_down['TradeSellNo'].isin(transaction_df_down_big.index)]#
    ptail = transaction_df_down.groupby('TradeSellNo')['TradePrice'].min()
    phead = transaction_df_down.groupby('TradeSellNo').head(1)[['TradeSellNo', 'last_price']].set_index('TradeSellNo')['last_price']
    if transaction_df_down.empty:
        power_2 = np.nan
    else:
        ret = (ptail - phead) / transaction_df_down['pre_close'][0]
        if abs(ret.sum()) < 0.001:
            ret_sum = 0.001
        else:
            ret_sum = ret.sum()
        power_2 = transaction_df_down['TradeMoney'].sum() / ret_sum / 100
    factor_dict = {factor_name: power_2/mv}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
