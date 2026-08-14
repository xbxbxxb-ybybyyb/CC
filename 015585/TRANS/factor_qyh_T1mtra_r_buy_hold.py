# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：主买遭遇托单的程度
# 6，3，0.01
# pj2_jhjj_volume_zb
factor_name = 'qyh_T1mtra_r_buy_hold'
def factor_qyh_T1mtra_r_buy_hold(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    mv = transaction_df['pre_close'][0] * transaction_df['ff_shares'][0]
    transaction_df['last_price'] = transaction_df['TradePrice'].shift(1) # 上一单成交价格
    pre = transaction_df['pre_close'][0]# 昨日收盘
    transaction_df_up = transaction_df[transaction_df['TradeBSFlag'] == 1]# 只看主动买入
    # 每一单的正常拉升幅度:基准选上一单的最后成交价格
    ptail = transaction_df_up.groupby('TradeBuyNo')['TradePrice'].max()
    phead = transaction_df_up.groupby('TradeBuyNo').head(1)[['TradeBuyNo', 'last_price']].set_index('TradeBuyNo')['last_price']
    if transaction_df_up.empty:
        ret_1 = np.nan
    else:
        ret_1 = (ptail - phead).sum() / pre
    # 每一单的单内拉升幅度:
    power_2 = transaction_df_up.groupby('TradeBuyNo')['TradePrice'].max() - transaction_df_up.groupby('TradeBuyNo')['TradePrice'].min()
    ret_2 = power_2.sum() / pre
    factor_dict = {factor_name: (ret_2 - ret_1) * 100000 /mv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
