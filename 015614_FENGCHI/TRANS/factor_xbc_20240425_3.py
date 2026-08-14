import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax



def factor_xbc_20240425_3(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240425_3'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]
    transaction_df1 = transaction_df[transaction_df['MDTime'] >= 93020000]
    transaction_df2 = transaction_df[transaction_df['MDTime'] <= 93020000]
    transaction_df1['stat'] = transaction_df1['TradeQty']
    transaction_df2['stat'] = transaction_df2['TradeQty']
    buy_money1 = transaction_df1.groupby('TradeBuyNo').sum()['stat']
    sell_money1 = transaction_df1.groupby('TradeSellNo').sum()['stat']
    buy_money2 = transaction_df2.groupby('TradeBuyNo').sum()['stat']
    sell_money2 = transaction_df2.groupby('TradeSellNo').sum()['stat']
    buy_stat1 = np.log(buy_money1.mean()+1)
    sell_stat1 = np.log(sell_money1.mean()+1)
    buy_stat2 = np.log(buy_money2.mean() + 1)
    sell_stat2 = np.log(sell_money2.mean() + 1)
    res = (buy_stat1-sell_stat1)/(buy_stat1+sell_stat1) * (buy_stat2-sell_stat2)/(buy_stat2+sell_stat2)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
