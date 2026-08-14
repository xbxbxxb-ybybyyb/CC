import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax





def factor_xbc_20240509_3(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240509_3'
    if return_fillna_dic:
        # 返回因子为 nan 时的填充值
        return {factor_name: 0.48}

    transaction_df = transaction_df[transaction_df['MDTime'] >= 92500000]  #
    transaction_df = transaction_df[transaction_df['MDTime'] <= 93030000]  #
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0) & (transaction_df['TradeMoney'] > 0)]      #

    ###############################
    transaction_df2 = transaction_df[(transaction_df['TradeBSFlag'] == 1) | (transaction_df['TradeBSFlag'] == 0)]
    score = np.nan
    if len(transaction_df2) > 0:
        TradeSellNo_num = transaction_df2.groupby('TradeSellNo')['TradeSellNo'].count()
        lim= 10
        TradeSellNo_num[TradeSellNo_num>lim] = lim
        score = np.std(np.log(1+TradeSellNo_num))
    factor_dict = {factor_name: score}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

