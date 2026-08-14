# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：主卖遭遇托单的程度(<0)，负的越多，抵抗越激烈
# gg
factor_name = 'qyh_T1mtra_r_sell_hold'
def factor_qyh_T1mtra_r_sell_hold(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    transaction_df['last_price'] = transaction_df['TradePrice'].shift(1) # 上一单成交价格
    pre = transaction_df['pre_close'][0]# 昨日收盘
    mv = transaction_df['pre_close'][0] * transaction_df['ff_shares'][0]
    transaction_df_down = transaction_df[transaction_df['TradeBSFlag'] == 2]# 只看主动卖出
    # 每一单的正常砸盘幅度:基准选上一单的最后成交价格
    ptail = transaction_df_down.groupby('TradeSellNo')['TradePrice'].min()
    phead = transaction_df_down.groupby('TradeSellNo').head(1)[['TradeSellNo', 'last_price']].set_index('TradeSellNo')['last_price']
    if transaction_df_down.empty:
        ret_1 = np.nan
    else:
        ret_1 = (ptail - phead).sum() / pre
    # 每一单的单内砸盘幅度:
    power_2 = transaction_df_down.groupby('TradeSellNo')['TradePrice'].min() - transaction_df_down.groupby('TradeSellNo')['TradePrice'].max()
    ret_2 = power_2.sum() / pre
    factor_dict = {factor_name: (ret_2 - ret_1) * 100000/mv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
