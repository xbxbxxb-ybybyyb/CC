import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax



def factor_xbc_20240118_9(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240118_9'
    if return_fillna_dic:
        # 返回因子为 nan 时的填充值
        return {factor_name: 0}

    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0) & (transaction_df['TradeMoney'] > 0)]      #

    transaction_df1 = transaction_df[transaction_df['TradeBSFlag'] == 1]
    transaction_df2 = transaction_df[transaction_df['TradeBSFlag'] == 2]
    score = len(set(transaction_df1['TradeBuyNo']))**2- (len(set(transaction_df2['TradeSellNo'])))**2
    ###############################
    factor_dict = {factor_name: score}
    ###############################
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
