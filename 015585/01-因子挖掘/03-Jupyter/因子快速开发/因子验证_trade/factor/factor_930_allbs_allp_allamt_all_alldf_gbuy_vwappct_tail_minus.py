import numpy as np
import pandas as pd
import decimal
from functions import *
factor_name = '930_allbs_allp_allamt_all_alldf_gbuy_vwappct_tail_minus'#
def factor_930_allbs_allp_allamt_all_alldf_gbuy_vwappct_tail_minus(trade_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    factor_explain = "930_allbs_allp_allamt_all_alldf_gbuy_vwappct_tail_minus"
    dt, ticker = trade_df.index[0]
    zcz = ((ticker[0:2] == '30') & (dt >= pd.Timestamp('20200824'))) | (ticker[0:2] == '68')
    if zcz:
        trade_df['trade_price'] = ((trade_df['trade_price']/trade_df['pre_close'] - 1)/2 + 1) * trade_df['pre_close']
    trade_df['TradeAmt'] = trade_df['TradeMoney']
    trade_df = trade_df[trade_df['TradePrice'] > 0]
    trade_df = trade_df[trade_df['MDTime'] >= 93000000]
    trade_df['TradeAmt'] = (trade_df['TradePrice'] * trade_df['TradeQty']).apply(lambda x: round_(x, 5))

    trade_df['factor'] = trade_df['TradeAmt'].cumsum() / trade_df['TradeQty'].cumsum() / trade_df['pre_close'] - 1
    trade_df = trade_df.groupby('TradeBuyNo')['factor'].sum().to_frame(name = 'factor')
    res = f_calc_tail(trade_df['factor'])
    
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)
