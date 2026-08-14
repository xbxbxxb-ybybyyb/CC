# coding: utf-8
# Author：fengchi863
# Date ：2023/3/22 10:19
import pandas as pd

def factor_fc_call_b_m_deal_pct(transaction_df, return_fillna_dic=False):
    factor_name = 'fc_call_b_m_deal_pct'

    if return_fillna_dic:
        return {factor_name: 0}
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0)]  # 去除撤单
    transaction_df = transaction_df[transaction_df['MDTime'] < 93000000]
    transaction_df = transaction_df.query('TradeBuyNo > TradeSellNo')

    middle_deal_df = transaction_df.query('TradeMoney < 200000 & TradeMoney > 50000')
    try:
        ret = middle_deal_df['TradeMoney'].sum() / transaction_df['TradeMoney'].sum()
    except:
        ret = 0

    factor = ret
    factor_dict = {factor_name: factor}

    return pd.Series(factor_dict)