import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax



def factor_xbc_20240229_8(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240229_8'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]
    buy_money = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']
    sell_money = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    if sell_money.mean() <= 0.001:
        amt_per_tran = np.nan
    else:
        buy_stat = np.log(buy_money.mean()+1)
        sell_stat = np.log(sell_money.mean()+1)
        amt_per_tran = (buy_stat-sell_stat)/(buy_stat+sell_stat)
    factor_dict = {factor_name: amt_per_tran}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
