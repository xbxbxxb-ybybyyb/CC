import numpy as np
import pandas as pd
import decimal
from functions import *
factor_name = '1m_buy_allp_big_t100_alldf_calc_amt2mv_min_minus'#
def factor_1m_buy_allp_big_t100_alldf_calc_amt2mv_min_minus(trade_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    factor_explain = "1m_buy_allp_big_t100_alldf_calc_amt2mv_min_minus"
    dt, ticker = trade_df.index[0]
    zcz = ((ticker[0:2] == '30') & (dt >= pd.Timestamp('20200824'))) | (ticker[0:2] == '68')
    if zcz:
        trade_df['trade_price'] = ((trade_df['trade_price']/trade_df['pre_close'] - 1)/2 + 1) * trade_df['pre_close']
    trade_df['TradeAmt'] = trade_df['TradeMoney']
    trade_df = trade_df[trade_df['TradePrice'] > 0]
    trade_df = trade_df[trade_df['MDTime'] >= 93000000]
    trade_df['TradeAmt'] = (trade_df['TradePrice'] * trade_df['TradeQty']).apply(lambda x: round_(x, 5))

    max_time = trade_df['MDTime'].max()
    time_start = fun_get_time(max_time,-60)
    trade_df = trade_df[trade_df['MDTime'] >= time_start]
    
    trade_df = trade_df.tail(100)
    trade_df = trade_df[trade_df['TradeBSFlag'] == 1]
    groupby_buy = trade_df.groupby('TradeBuyNo')['TradeAmt'].sum()
    groupby_buy = groupby_buy[groupby_buy >= 200000]
    big_buy_list = list(groupby_buy.index)
    trade_df = trade_df[trade_df['TradeBuyNo'].isin(big_buy_list)]
    trade_df['factor'] = trade_df['TradeAmt'] / trade_df['pre_close'] / trade_df['ff_shares']
    res = f_calc_min(trade_df['factor'])
    
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)
