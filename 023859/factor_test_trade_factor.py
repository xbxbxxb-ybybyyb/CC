# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_test_trade_factor(transaction_df, return_fillna_dic=False):
    factor_name = 'test_trade_factor'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df=transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    transaction_df = transaction_df[transaction_df['MDTime'] >=93000000] #选择连续竞价阶段
    amt = transaction_df['TradeMoney'].sum()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

def factor_big_order_buy_strength(data, return_fillna_dic=False):
    factor_name = 'factor_big_order_buy_strength'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # transaction_df=transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    data = data[(data['MDTime']>=93000000)&(data['MDTime']<=145700000)]
    df_buy = data.groupby('TradeBuyNo')['TradeMoney'].sum()
    BigOrderNum = df_buy[df_buy >= 200000].index
    df_bigorder = data[data['TradeBuyNo'].isin(BigOrderNum)]
    if len(df_bigorder):
        amt = (df_bigorder['TradeBSFlag'] == 1).sum() / len(df_bigorder)
    else:
        amt = 0
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

def factor_big_order_sell_strength(data, return_fillna_dic=False):
    factor_name = 'factor_big_order_sell_strength'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # transaction_df=transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    data = data[(data['MDTime']>=93000000)&(data['MDTime']<=145700000)]
    df_sell = data.groupby('TradeSellNo')['TradeMoney'].sum()
    BigOrderNum = df_sell[df_sell >= 200000].index
    df_sellbigorder = data[data['TradeSellNo'].isin(BigOrderNum)]
    if len(df_sellbigorder):
        amt = (df_sellbigorder['TradeBSFlag'] == 2).sum() / len(df_sellbigorder)
    else:
        amt = 0
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


def factor_small_order_buy_strength(data, return_fillna_dic=False):
    factor_name = 'factor_small_order_buy_strength'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # transaction_df=transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    data = data[(data['MDTime'] >= 93000000) & (data['MDTime'] <= 145700000)]
    df_buy = data.groupby('TradeBuyNo')['TradeMoney'].sum()
    BuySmallOrderNum = df_buy[df_buy < 50000].index
    df_buysmallorder = data[data['TradeBuyNo'].isin(BuySmallOrderNum)]

    if len(df_buysmallorder):
        amt = (df_buysmallorder['TradeBSFlag'] == 1).sum() / len(df_buysmallorder)
    else:
        amt = 0
    factor_dict = {factor_name: amt}

    return pd.Series(factor_dict)

def factor_small_order_sell_strength(data, return_fillna_dic=False):
    factor_name = 'factor_small_order_sell_strength'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # transaction_df=transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    data = data[(data['MDTime'] >= 93000000) & (data['MDTime'] <= 145700000)]
    df_sell = data.groupby('TradeSellNo')['TradeMoney'].sum()
    SellSmallOrderNum = df_sell[df_sell < 50000].index
    df_sellsmallorder = data[data['TradeSellNo'].isin(SellSmallOrderNum)]

    if len(df_sellsmallorder):
        amt = (df_sellsmallorder['TradeBSFlag'] == 2).sum() / len(df_sellsmallorder)
    else:
        amt = 0

    factor_dict = {factor_name: amt}

    return pd.Series(factor_dict)

def factor_middle_order_buy_strength(data, return_fillna_dic=False):
    factor_name = 'factor_middle_order_buy_strength'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # transaction_df=transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    data = data[(data['MDTime'] >= 93000000) & (data['MDTime'] <= 145700000)]
    df_buy = data.groupby('TradeBuyNo')['TradeMoney'].sum()
    BuyMidOrderNum = df_buy[(df_buy >= 50000)&(df_buy < 200000)].index
    df_buymidorder = data[data['TradeBuyNo'].isin(BuyMidOrderNum)]

    if len(df_buymidorder):
        amt = (df_buymidorder['TradeBSFlag'] == 1).sum() / len(df_buymidorder)
    else:
        amt = 0
    factor_dict = {factor_name: amt}

    return pd.Series(factor_dict)

def factor_middle_order_sell_strength(data, return_fillna_dic=False):
    factor_name = 'factor_middle_order_sell_strength'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # transaction_df=transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    data = data[(data['MDTime'] >= 93000000) & (data['MDTime'] <= 145700000)]
    df_sell = data.groupby('TradeSellNo')['TradeMoney'].sum()
    SellMidOrderNum = df_sell[(df_sell >= 50000)&(df_sell < 200000)].index
    df_sellmidorder = data[data['TradeSellNo'].isin(SellMidOrderNum)]

    if len(df_sellmidorder):
        amt = (df_sellmidorder['TradeBSFlag'] == 2).sum() / len(df_sellmidorder)
    else:
        amt = 0
    factor_dict = {factor_name: amt}

    return pd.Series(factor_dict)


def factor_bds_order_buy_strength(data, return_fillna_dic=False):
    factor_name = 'factor_bds_order_buy_strength'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # transaction_df=transaction_df[(transaction_df['TradePrice']>0)] #去除撤单
    data = data[(data['MDTime']>=93000000)&(data['MDTime']<=145700000)]
    df_buy = data.groupby('TradeBuyNo')['TradeMoney'].sum()
    BigOrderNum = df_buy[df_buy >= 200000].index
    BuySmallOrderNum = df_buy[df_buy < 50000].index
    df_buybigorder = data[data['TradeBuyNo'].isin(BigOrderNum)]
    df_buysmallorder = data[data['TradeBuyNo'].isin(BuySmallOrderNum)]
    if len(df_buybigorder):
        amt_big = (df_buybigorder['TradeBSFlag'] == 1).sum() / len(df_buybigorder)
    else:
        amt_big = 0
    if len(df_buysmallorder):
        amt_small = (df_buysmallorder['TradeBSFlag'] == 1).sum() / len(df_buysmallorder)
    else:
        amt_small = 0
    amt = amt_big / (amt_small+1e-8)
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

def factor_time_weighted_amount(data, return_fillna_dic=False):
    factor_name = 'factor_time_weighted_amount'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    data = data[(data['MDTime'] >= 93000000)]
    data = data[(data['TradePrice'] > 0)]  # 去除撤单
    amt = np.sum(data['TradeMoney'] * data['MDTime'].diff())/60000
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

def factor_time_weighted_buy_amount(data, return_fillna_dic=False):
    factor_name = 'factor_time_weighted_buy_amount'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    data = data[(data['MDTime'] >= 93000000)]
    data = data[(data['TradePrice'] > 0)&(data['TradeBSFlag'] == 1)]  # 去除撤单
    amt = np.sum(data['TradeMoney'] * data['MDTime'].diff())/60000
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

def factor_time_weighted_sell_amount(data, return_fillna_dic=False):
    factor_name = 'factor_time_weighted_sell_amount'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    data = data[(data['MDTime'] >= 93000000)]
    data = data[(data['TradePrice'] > 0)&(data['TradeBSFlag'] == 2)]  # 去除撤单
    amt = np.sum(data['TradeMoney'] * data['MDTime'].diff())/60000
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

def factor_price_diff(data, return_fillna_dic=False):
    factor_name = 'factor_price_diff'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    data = data[(data['MDTime'] >= 93000000)]
    data['MidPrice'] = (data['WeightedAvgBidPx'] + data['WeightedAvgOfferPx']) / 2
    data['avgpx'] = data['amt'] / data['vol']
    amt = np.mean((data['avgpx'] - data['MidPrice']) / (data['avgpx'] + data['MidPrice'])*(data['OpenPx']/data['PreClosePx']-1))
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


def factor_amt_std(data, return_fillna_dic=False):
    factor_name = 'factor_amt_std'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    data = data[(data['MDTime'] >= 93000000)]
    amt = np.std(data['amt'])
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

def factor_(data, return_fillna_dic=False):
    factor_name = 'factor_amt_std'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    data = data[(data['MDTime'] >= 93000000)]
    amt = np.std(data['amt'])
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)