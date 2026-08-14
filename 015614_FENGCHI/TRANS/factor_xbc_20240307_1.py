import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax



def factor_xbc_20240307_1(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240307_1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.3}

    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]

    buy_money = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']
    buy_money_small = buy_money[buy_money <= 200000]
    sell_money = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    sell_money[sell_money > 1000000] = 1000000
    sell_money_big = sell_money[sell_money >= 500000]
    stat = buy_money_small.sum() + sell_money_big.sum()
    # ratio
    if abs(buy_money.sum()) <= 0.001:
        ratio = np.nan
    else:
        ratio = stat / buy_money.sum()
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

