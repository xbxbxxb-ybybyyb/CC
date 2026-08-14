# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 0216提交
# 逻辑：大单中每个主动卖单的金额/拉升幅度（基于单内价格）:GG
# score:3,-0.02
# 0
factor_name = 'qyh_T1mtra_r_amt2pct_down_big'#
def factor_qyh_T1mtra_r_amt2pct_down_big(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.2}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    mv = transaction_df['pre_close'][0] * transaction_df['ff_shares'][0]
    # 每一单的拉升幅度:基准选上一单的最后成交价格
    transaction_df_down = transaction_df[transaction_df['TradeBSFlag'] == 2]# 只看主动卖出
    transaction_df_down_big = transaction_df_down.groupby('TradeSellNo')['TradeMoney'].sum()
    transaction_df_down_big = transaction_df_down_big[transaction_df_down_big > 200000]# 大单
    transaction_df_down = transaction_df_down[transaction_df_down['TradeSellNo'].isin(transaction_df_down_big.index)]# 只要大单部分
    ptail = transaction_df_down.groupby('TradeBuyNo')['TradePrice'].min()
    phead = transaction_df_down.groupby('TradeBuyNo')['TradePrice'].max()
    if transaction_df_down.empty:
        power_2 = np.nan
    else:
        ret = (ptail - phead) / transaction_df_down['pre_close'][0]
        power_2 = transaction_df_down['TradeMoney'].sum() / ret.sum() / 100
    factor_dict = {factor_name: power_2/mv}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
