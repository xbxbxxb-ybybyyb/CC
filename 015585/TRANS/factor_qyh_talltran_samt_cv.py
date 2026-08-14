# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_qyh_talltran_samt_cv(transaction_df, return_fillna_dic=False):
    factor_name = 'qyh_talltran_samt_cv'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.95}
    # mv = transaction_df['pre_close'].max() * transaction_df['ff_shares'].max()
    transaction_df = transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    transaction_df = transaction_df[transaction_df['MDTime'] >=93000000] #选择连续竞价阶段
    # sell_big
    sell_big = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    sell_big = sell_big[sell_big > 200000]
    cv = sell_big.std() / abs(sell_big.mean()) if abs(sell_big.mean()) > 0 else np.nan
    factor_dict = {factor_name: cv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

