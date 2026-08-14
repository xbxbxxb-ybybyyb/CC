import numpy as np
import pandas as pd
import decimal
from functions import *
factor_name = '1m_allbs_allp_allamt_all_alldf_calcbuybs_amt2buypctdiff_sum_minus'#
def factor_1m_allbs_allp_allamt_all_alldf_calcbuybs_amt2buypctdiff_sum_minus(trade_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    factor_explain = "1m_allbs_allp_allamt_all_alldf_calcbuybs_amt2buypctdiff_sum_minus"
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
    
    trade_df['max_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('max')
    trade_df['min_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('min')
    trade_df['factor'] = trade_df['TradeAmt'] / ((trade_df['max_price'] + 1e-2 - trade_df['min_price'])/trade_df['pre_close'])
    trade_df = trade_df.groupby('TradeBuyNo')['factor','TradeMoney'].sum()
    trade_df1 = trade_df[trade_df['TradeMoney'] >= 200000]
    trade_df2 = trade_df[trade_df['TradeMoney'] < 50000]
    res1 = f_calc_sum(trade_df1['factor'])
    res2 = f_calc_sum(trade_df2['factor'])
    res = res1 - res2
    
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)
