import numpy as np
import pandas as pd
import decimal
factor_name = 'ttrade_sample'#
def factor_qyh_ttrade_sample(trade_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    factor_explain = "1m_buy_up9_big_t50_bsdf_calc_vwappct_kurt_minus"
    dt, ticker = trade_df.index[0]
    zcz = ((ticker[0:2] == '30') & (dt >= 20200824)) | (ticker[0:2] == '68')
    if zcz:
        trade_df['trade_price'] = ((trade_df['trade_price']/trade_df['pre_close'] - 1)/2 + 1) * trade_df['pre_close']
    max_time = trade_df['MDTime'].max()
    time_start = fun_get_time(max_time,-60)
    trade_df = trade_df[trade_df['MDTime'] >= time_start]

    trade_df = trade_df.tail(50)
    trade_df = trade_df[trade_df['TradeBSFlag'] == 1]
    price9 = trade_df['pre_close'] * 1.09
    trade_df = trade_df[trade_df['TradePrice'] >= price9]
    groupby_buy = trade_df.groupby('TradeBuyNo')['TradeAmt'].sum()
    groupby_buy = groupby_buy[groupby_buy >= 200000]
    big_buy_list = list(groupby_buy.index)
    trade_df = trade_df[trade_df['TradeBuyNo'].isin(big_buy_list)]
    trade_df['factor'] = trade_df['TradeAmt'].cumsum() / trade_df['TradeQty'].cumsum() / trade_df['pre_close'] - 1
    trade_df1 = trade_df[trade_df['TradeBSFlag'] == 1]
    trade_df2 = trade_df[trade_df['TradeBSFlag'] == 2]
    res1 = f_calc_kurt(trade_df1['factor'])
    res2 = f_calc_kurt(trade_df2['factor'])
    res = res1 - res2
    
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)
