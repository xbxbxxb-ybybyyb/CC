import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax



def factor_xbc_20240314_3(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240314_3'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]
    # buy
    buy_stat = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']
    buy_stat = buy_stat.tail(int(len(buy_stat)/2))
    std_per_tran_in = buy_stat.std()-buy_stat.mean()
    factor_dict = {factor_name: std_per_tran_in}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
