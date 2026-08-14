# coding: utf-8
# Author：fengchi863
# Date ：2023/3/22 10:26

import pandas as pd

def factor_fc_call_s_m_num_ratio(transaction_df, return_fillna_dic=False):
    factor_name = 'fc_call_s_m_num_ratio'

    if return_fillna_dic:
        return {factor_name: 0}
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0)]
    transaction_df = transaction_df[transaction_df['MDTime'] < 93000000]
    transaction_df = transaction_df.query('TradeMoney >= 50000 & TradeMoney < 200000')
    sell_df = transaction_df.query('TradeBuyNo < TradeSellNo')

    if transaction_df.shape[0] != 0:
        ret = sell_df.shape[0] / transaction_df.shape[0]
    else:
        ret = 0

    factor = ret
    factor_dict = {factor_name: factor}

    return pd.Series(factor_dict)