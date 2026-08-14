# -*- coding: utf-8 -*-
# @Time    : 2023/02/28 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_T1mtra_r_amt2pct_down_ln'#
def factor_qyh_T1mtra_r_amt2pct_down_ln(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    transaction_df['last_price'] = transaction_df['TradePrice'].shift(1) # 上一单成交价格
    # mv = transaction_df['pre_close'][0] * transaction_df['ff_shares'][0]
    # 每一单的砸盘幅度:基准选上一单的最后成交价格
    transaction_df_down = transaction_df[transaction_df['TradeBSFlag'] == 2]# 只看主动卖出
    ptail = transaction_df_down.groupby('TradeSellNo')['TradePrice'].min()
    phead = transaction_df_down.groupby('TradeSellNo').head(1)[['TradeSellNo', 'last_price']].set_index('TradeSellNo')['last_price']
    if transaction_df_down.empty:
        power_2 = np.nan
    else:
        ret = (ptail - phead) / transaction_df_down['pre_close'][0]
        power_2 = np.log(transaction_df_down['TradeMoney'].sum()) / ret.sum() / 100
    factor_dict = {factor_name: power_2}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
