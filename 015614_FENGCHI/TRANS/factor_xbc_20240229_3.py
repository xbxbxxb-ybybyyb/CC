import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax



def factor_xbc_20240229_3(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240229_3'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0]
    transaction_df['TradePrice0'] = transaction_df['TradePrice'].shift(1)
    transaction_df_down = transaction_df[transaction_df['TradeBSFlag'] == 2]
    price2 = transaction_df_down.groupby('TradeSellNo')['TradePrice'].min()
    price1 = transaction_df_down.groupby('TradeSellNo').head(1)[['TradeSellNo', 'TradePrice0']].set_index('TradeSellNo')['TradePrice0']
    if transaction_df_down.empty:
        ret = np.nan
        amt = np.nan
    else:
        ret = (price2 - price1) / transaction_df_down['pre_close'][0]
        amt = transaction_df_down['TradeMoney'].sum()
        ret = abs(ret.sum())
    if ret > 0.001:
        factor_dict = {factor_name: (amt)/(ret)}
    else:
        factor_dict = {factor_name: np.nan}
    return pd.Series(factor_dict)
